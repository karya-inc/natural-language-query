import React from 'react';
import { ParameterForm } from 'src/helpers/parameter-spec/src/Index';
import { UseFormReturn } from '../hooks/useForm';
import _ from 'lodash';
import { DefinitionRendererConfig } from './ParameterDefinitionRenderer';
import { SectionRendererBuilder } from './SectionRenderer';

export interface FormRendererConfig {
  components: DefinitionRendererConfig;
}

export interface FormRendererProps {
  ctx: UseFormReturn<any>['ctx'];
  parameters?: ParameterForm<any>;
}

export function FormRendererBuilder(config: FormRendererConfig) {
  const { FormContainer = React.Fragment } = config.components;
  const SectionRenderer = SectionRendererBuilder(config);

  return React.memo((props: FormRendererProps) => {
    let { ctx, parameters } = props;
    if (!parameters) {
      parameters = ctx.parameters;
    }
    return (
      <FormContainer>
        {parameters.map((section, index) => (
          <SectionRenderer ctx={props.ctx} section={section} key={index} />
        ))}
      </FormContainer>
    );
  });
}
