// Copyright (c) DAIA Tech Pvt Ltd
//
// Default button theme

import { ColorMap } from '../Attributes';
import { KaryaButtonTheme } from '../ButtonVariants';

export const buttonTheme: KaryaButtonTheme = {
  submit: {
    type: 'submit',
    backgroundColor: ColorMap.primary,
    textColor: ColorMap.white,
    _disabled: {
      backgroundColor: ColorMap.stockGray,
    },
  },
  secondary: {
    backgroundColor: ColorMap.primaryDark,
    textColor: ColorMap.white,
  },
  secondary_light: {
    backgroundColor: ColorMap.white,
    textColor: ColorMap.primaryDark,
  },
  secondary_outlined: {
    borderColor: ColorMap.primaryDark,
    borderWidth: '1px',
    textColor: ColorMap.primaryDark,
  },
  secondary_outlined_light: {
    borderColor: ColorMap.white,
    borderWidth: '1px',
    textColor: ColorMap.white,
  },
};
