import { InputHTMLAttributes, ReactNode } from 'react';

export type BaseInputProps = {
  label?: string;
  description?: string;
  error?: string;
  isRequired?: boolean;
  isDisabled?: boolean;
  isInvalid?: boolean;
};

export type InputProps = BaseInputProps & InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement>;

export type StringInputProps = {
  long?: boolean;
  placeholder?: string;
} & InputProps;

export type SwitchProps = {
  isChecked?: boolean;
} & InputProps;

export type ListInputProps = {
  onChange: (id: string, value: string[]) => void;
  delimiters?: string[];
  value: string[];
} & Omit<InputProps, 'value' | 'onChange'>;

export type SelectProps = {
  options: { [key: string]: string };
  onChange: (id: string, value: string) => void;
} & BaseInputProps &
  Omit<InputHTMLAttributes<HTMLSelectElement>, 'onChange'>;

export type MultiSelectProps = {
  options: { [key: string]: string };
  onChange: (id: string, value: string[]) => void;
  value: string[];
} & Omit<SelectProps, 'value' | 'onChange'>;

export type ComponentWithChildrenProps = {
  children: ReactNode;
};

export type SectionContainerProps = {
  label: string;
  description?: string;
  children: JSX.Element[];
};

export type FileInputProps = {
  value: File;
} & InputProps;

export type MultiFileInputProps = {
  onChange: (id: string, value: File[]) => void;
  value: File[];
  showFileNames?: boolean;
} & Omit<FileInputProps, 'value' | 'onChange'>;

export type CustomInputRendererProps = {
  id: string;
  form: Record<string, any>;
  errors: Record<string, any>;
  setFormField: (id: string, value: any) => void;
} & InputProps;
