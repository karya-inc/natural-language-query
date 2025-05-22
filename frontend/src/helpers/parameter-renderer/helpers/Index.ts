import { RendererInfo } from '../hooks';
import { FormInputRenderer } from '../types/CustomRenderer';

export function typedRendererInfo<Props extends Record<string, any>>(info: {
  type: string;
  component: FormInputRenderer<Props, any>;
  props: Props;
}): RendererInfo<Props> {
  return info;
}
