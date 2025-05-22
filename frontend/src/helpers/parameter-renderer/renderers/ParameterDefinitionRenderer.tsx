import { ParameterDefinition } from '@karya/parameter-specs';
import {
  FileInputProps,
  ListInputProps,
  MultiFileInputProps,
  MultiSelectProps,
  SectionContainerProps,
  SelectProps,
  StringInputProps,
  SwitchProps,
} from '../types/InputComponentProps';
import React, { PropsWithChildren, useEffect, useMemo } from 'react';
import { UseFormReturn } from '../hooks/useForm';
import _ from 'lodash';

export interface DefinitionRendererConfig {
  FormContainer?: React.FC<PropsWithChildren>;
  SectionContainer: React.FC<SectionContainerProps>;
  Input: React.FC<StringInputProps>;
  ListInput: React.FC<ListInputProps>;
  File: React.FC<FileInputProps>;
  MultiFile: React.FC<MultiFileInputProps>;
  Select: React.FC<SelectProps>;
  MultiSelect: React.FC<MultiSelectProps>;
  Switch: React.FC<SwitchProps>;
}

export interface DefinitionRendererProps {
  parameter: ParameterDefinition<any>;
  // @ts-ignore
  ctx: UseFormReturn<any>['ctx'];
  opts?: Partial<{
    errorId: string;
  }>;
}

export function DefinitionRendererBuilder(Components: DefinitionRendererConfig) {
  const ParameterDefinitionRenderer = React.memo(
    ({ parameter, ctx, opts }: DefinitionRendererProps) => {
      const { id, type, required, label, description, renderer, extraProps } = parameter;
      const {
        form,
        errors,
        handleChange,
        handleListChange,
        handleBooleanChange,
        handleFileChange,
        handleMultiFileChange,
        handleJsonChange,
        renderers,
        setFormField,
      } = ctx;
      const value = form[id];
      const error = errors[opts?.errorId ?? id] ?? undefined;
      let isRequirementsSatisfied = true;
      let isRequired = required;

      if ('requires' in parameter && parameter.requires) {
        isRequirementsSatisfied = parameter.requires.reduce((acc, [key, reference, type]) => {
          let fieldState = ctx.form[key];
          let isRequirementSatisfied: boolean;

          type = type ?? 'EQUALS';
          switch (type) {
            case 'EQUALS':
              if (reference == false && fieldState == undefined) {
                isRequirementSatisfied = true;
              } else {
                isRequirementSatisfied = fieldState == reference;
              }
              break;
            case 'NOT_EQUALS':
              isRequirementSatisfied = fieldState != reference;
              break;

            case 'IN':
              isRequirementSatisfied = reference.includes(fieldState);
              break;

            case 'NOT_IN':
              isRequirementSatisfied = !reference.includes(fieldState);
              break;
          }
          return acc && isRequirementSatisfied;
        }, true);
        if (isRequirementsSatisfied && parameter.requiredIfSatisfied) {
          isRequired = true;
        }
      }

      const isDisabled = !isRequirementsSatisfied;
      let rendererParams = {
        id,
        value,
        label,
        error,
        description,
        isRequired,
        isDisabled,
        isInvalid: error !== undefined,
      };

      if (ctx.hideDisabledFields && isDisabled) {
        return null;
      }

      if (extraProps) {
        rendererParams = { ...rendererParams, ...extraProps };
      }

      const matchingRenderer = useMemo(() => {
        if (!renderer) {
          return null;
        }
        const match = renderers?.find((curr) => curr.type === renderer) ?? null;
        if (match == null) {
          console.warn(`Renderer with name "${renderer}" was required by parameter with ID "${id}", but was not found`);
        }
        return match;
      }, [renderer, renderers]);

      if (matchingRenderer) {
        return (
          <matchingRenderer.component
            form={form as any}
            errors={errors}
            setFormField={setFormField}
            {...rendererParams}
            {...matchingRenderer.props}
          />
        );
      }

      useEffect(() => {
        if (parameter.type === 'fixed' && form[id] !== parameter.value) {
          setFormField(id, parameter.value);
        }
      }, [parameter.type, form[id]]);

      switch (parameter.type) {
        case 'string':
          return (
            <Components.Input
              {...rendererParams}
              value={value ?? ''}
              type={type}
              // @ts-ignore
              onChange={handleChange}
              long={parameter.long}
              placeholder={parameter.placeholder}
            />
          );
        case 'int':
        case 'float':
        case 'time':
        case 'date':
          // @ts-ignore
          return <Components.Input {...rendererParams} value={value ?? ''} type={type} onChange={handleChange} />;
        case 'boolean':
          // @ts-ignore
          return <Components.Switch {...rendererParams} isChecked={value ?? false} onChange={handleBooleanChange} />;
        case 'enum':
          return (
            <Components.Select
              {...rendererParams}
              value={value ?? ''}
              onChange={setFormField<string>}
              options={parameter.list}
            />
          );
        case 'enum_multi':
          return (
            <Components.MultiSelect
              {...rendererParams}
              value={value ?? []}
              onChange={handleListChange}
              options={parameter.list}
            />
          );
        case 'list':
          return (
            <Components.ListInput
              {...rendererParams}
              value={value ?? []}
              delimiters={parameter.delimiters}
              onChange={handleListChange}
            />
          );
        case 'file':
          return <Components.File {...rendererParams} onChange={handleFileChange} />;
        case 'json_array':
          if (parameter.items) {
            // Open up the array into individual parameters if items are defined
            return (
              <React.Fragment>
                {parameter.items.map((item, index) => {
                  // Generate a unique ID for each item based on index
                  const itemId = `${parameter.id}.${item.id}`;
                  const errorId = `${parameter.id}.${index}`;
                  return (
                    <ParameterDefinitionRenderer
                      ctx={ctx}
                      parameter={{ ...item, id: itemId }}
                      key={itemId}
                      opts={{ errorId }}
                    />
                  );
                })}
              </React.Fragment>
            );
          } else {
            return <Components.File {...rendererParams} value={value ?? []} onChange={handleJsonChange} />;
          }
        case 'json_object':
          return <Components.File {...rendererParams} value={value ?? {}} onChange={handleJsonChange} />;
        case 'json':
          return <Components.File {...rendererParams} value={value ?? null} onChange={handleJsonChange} />;
        case 'multi_file':
          return (
            <Components.MultiFile
              {...rendererParams}
              value={value ?? []}
              showFileNames={parameter.showFileNames}
              onChange={handleMultiFileChange}
            />
          );
        case 'fixed':
          return null;
      }
    },
    (prev, next) => {
      if (prev === next) return true;
      const {
        ctx: { form: prevForm, errors: prevErrors },
        parameter: prevParameter,
      } = prev;

      const {
        ctx: { form: nextForm, errors: nextErrors },
        parameter: nextParameter,
      } = next;

      if (prevParameter.renderer != undefined) {
        return false;
      }

      if (!_.isEqual(prevParameter, nextParameter)) {
        return false;
      }

      const prevId = prevParameter.id;
      const nextId = nextParameter.id;
      if (!_.isEqual(prevForm[prevId], nextForm[nextId])) {
        return false;
      }

      let isRequirementsChanged = false;
      if ('requires' in nextParameter) {
        nextParameter.requires?.forEach(([id, _require_val]) => {
          if (!_.isEqual(prevForm[id as string], nextForm[id as string])) {
            isRequirementsChanged = true;
            return;
          }
        });
      }

      if (isRequirementsChanged) {
        return false;
      }

      if (prevParameter.type === 'json_array' && prevParameter.items) {
        const itemsChanged = prevParameter.items.some(
          (item) => prevForm[`${nextId}.${item.id}`] !== nextForm[`${nextId}.${item.id}`],
        );
        return !itemsChanged;
      }

      if (prevErrors[prevId] !== nextErrors[nextId]) {
        return false;
      }
      return true;
    },
  );
  return ParameterDefinitionRenderer;
}
