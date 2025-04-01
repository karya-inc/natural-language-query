import { FileInputProps } from '../../../types/InputComponentProps';
import { InputContainer } from './FormInputContainer';
import { Button, HStack, Text } from '@chakra-ui/react';
import { useRef } from 'react';

export function FileInput(props: FileInputProps) {
  const { id, description, label, value, error, isInvalid, isDisabled, isRequired, size: _size, ...rest } = props;
  const inputRef = useRef<HTMLInputElement>(null);
  const handleBrowse = () => {
    inputRef.current?.click();
  };
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
      <input id={id} type="file" ref={inputRef} hidden {...rest} />
      <HStack spacing={5}>
        <Button variant="submit" isDisabled={isDisabled} onClick={handleBrowse}>
          Select File
        </Button>
        <Text>{value && value.name}</Text>
      </HStack>
    </InputContainer>
  );
}
