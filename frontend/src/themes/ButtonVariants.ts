// Copyright (c) DAIA Tech Pvt Ltd
//
// List of button variants. Every theme must define these variants

import { ButtonProps } from '@chakra-ui/react';

const ButtonVariants = ['submit', 'secondary', 'secondary_outlined'] as const;
type ButtonType = (typeof ButtonVariants)[number];

export type KaryaButtonTheme = { [key in ButtonType]: ButtonProps };
export const ButtonVariant: { [key in ButtonType]: key } = {
  submit: 'submit',
  secondary: 'secondary',
  secondary_outlined: 'secondary_outlined',
};
