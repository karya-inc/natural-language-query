import { StringInputProps } from '../../../types/InputComponentProps';
import { Input, Textarea } from '@chakra-ui/react';
import { InputContainer } from './FormInputContainer';

export function FormInput(props: StringInputProps) {
  const { id, description, long, label, error, isInvalid, isDisabled, isRequired, size: _size, ...rest } = props;
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
      {long ? <Textarea id={id} {...rest} /> : <Input id={id} {...rest} />}
    </InputContainer>
  );
}
