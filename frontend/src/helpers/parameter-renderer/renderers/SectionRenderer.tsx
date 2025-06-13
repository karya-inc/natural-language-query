import React from 'react';
import { DefinitionRendererBuilder } from './ParameterDefinitionRenderer';
import { ParameterDefinition, ParameterSection } from 'src/helpers/parameter-spec/src/Index';
import { UseFormReturn } from '../hooks';
import _ from 'lodash';
import { FormRendererConfig } from './FormRenderer';

export interface SectionRendererProps {
  ctx: UseFormReturn<any>['ctx'];
  section: ParameterSection<any>;
}
export function SectionRendererBuilder(config: FormRendererConfig) {
  const { SectionContainer } = config.components;
  const DefinitionRenderer = DefinitionRendererBuilder(config.components);
  return React.memo(
    (props: SectionRendererProps) => {
      return (
        <SectionContainer label={props.section.label} description={props.section.description}>
          {props.section.parameters.map((param) => (
            <DefinitionRenderer parameter={param} ctx={props.ctx} key={param.id} />
          ))}
        </SectionContainer>
      );
    },
    (prev, next) => {
      if (prev === next) return true;

      if (!_.isEqual(prev.section, next.section)) {
        return false;
      }

      const isSectionChanged = prev.section.parameters.some(
        // @ts-expect-error
        (def: Extract<ParameterDefinition<any>, { requires: Array<any> }>) => {
          if (def.type === 'json_array' && def.items) {
            return true;
          }
          const id = def.id as string;
          const valueChanged = !_.isEqual(prev.ctx.form[id], next.ctx.form[id]);
          const errorChanged = !_.isEqual(prev.ctx.errors[id], next.ctx.errors[id]);
          const requirementChanged = def.requires?.some(([key]) => prev.ctx.form[key] != next.ctx.form[key]);
          return valueChanged || errorChanged || requirementChanged;
        },
      );

      if (isSectionChanged) {
        return false;
      }

      const customRendererUsed = prev.section.parameters.some((def) => def.renderer !== undefined);
      if (customRendererUsed) {
        return false;
      }

      return true;
    },
  );
}
