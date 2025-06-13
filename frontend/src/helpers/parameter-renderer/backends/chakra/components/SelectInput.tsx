import { SelectProps } from '../../../types/InputComponentProps';
import { Select } from 'chakra-react-select';
import { InputContainer } from './FormInputContainer';
import { ButtonSelect } from './ButtonSelect';

export function SelectInput(props: SelectProps) {
  const {
    id,
    description,
    label,
    error,
    isInvalid,
    isDisabled,
    isRequired,
    options,
    size: _size,
    value,
    onChange,
  } = props;
  const numKeys = Object.keys(options).length;
  const isUseButtons = numKeys < 5;
  const reactSelectOptions = Object.keys(options).map((key) => ({ label: options[key], value: key }));
  return (
    <InputContainer
      id={id}
      description={description}
      label={label}
      error={error}
      isInvalid={isInvalid}
      isRequired={isRequired}
      isDisabled={isDisabled}
    >
      {isUseButtons || (
        <Select
          id={id}
          closeMenuOnSelect
          options={reactSelectOptions}
          value={{ label: options[value as keyof typeof options], value: (value as string) ?? '' }}
          onChange={(val) => onChange(id!, val?.value ?? '')}
        />
      )}
      {isUseButtons && (
        <ButtonSelect
          options={options}
          value={value as keyof typeof options}
          onChange={(val) => onChange(id!, val ?? '')}
          isDisabled={isDisabled}
        />
      )}
    </InputContainer>
  );
}
