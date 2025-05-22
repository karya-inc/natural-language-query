// Copyright (c) DAIA Tech Pvt Ltd
//
// Types for Custom Form Renderers

import { CustomInputRendererProps } from './InputComponentProps';

export type FormInputRenderer<RendererProps = {}, ExtraProps = {}> = React.FC<
  CustomInputRendererProps & RendererProps & ExtraProps
>;
