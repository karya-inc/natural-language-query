import { MultiSelectProps } from 'src/helpers/parameter-renderer/types/InputComponentProps';
import { InputContainer } from './FormInputContainer';
import { Select } from 'chakra-react-select';
import { ColorMap } from 'src/themes/Attributes';

export function MultiSelectInput(props: MultiSelectProps) {
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
    onChange,
    value,
  } = props;
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
      <Select
        isMulti
        selectedOptionStyle="check"
        hideSelectedOptions={false}
        closeMenuOnSelect={false}
        getOptionValue={(opt) => opt}
        getOptionLabel={(opt) => options[opt]}
        options={[{ label, options: Object.keys(options) }]}
        value={value}
        onChange={(val) => onChange(id!, val.slice(0))}
        placeholder="Select options"
        chakraStyles={{
          control: (provided) => ({
            ...provided,
            color: ColorMap.stockGray,
          }),
          menu: (provided) => ({
            ...provided,
            color: ColorMap.black,
          }),
          option: (provided) => ({
            ...provided,
            color: ColorMap.black,
          }),
        }}
      />
    </InputContainer>
  );
}
