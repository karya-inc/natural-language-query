import { ListInputProps } from '../../../../types/InputComponentProps';
import { HStack } from '@chakra-ui/react';
import { ChangeEventHandler, KeyboardEventHandler, useState } from 'react';
import { ListItem } from './ListItem';
import { FormInput } from '../FormInput';
import { InputContainer } from '../FormInputContainer';

export function ListInput(props: ListInputProps) {
  const {
    description,
    value,
    onChange,
    id,
    label,
    error,
    isInvalid,
    isRequired,
    isDisabled,
    delimiters,
    size: _size,
    ...rest
  } = props;
  const [inputValue, setInputValue] = useState('');
  const handleInputChange: ChangeEventHandler<HTMLInputElement> = (e) => {
    setInputValue(e.target.value);
  };
  const handleAddTag: KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === 'Enter' || delimiters?.includes(e.key)) {
      e.preventDefault();
      if (inputValue) {
        onChange(id!, [...value, inputValue.trim()]);
        setInputValue('');
      }
    }
  };
  const handleRemoveTag = (tagToRemove: string) => {
    const updatedList = value.filter((tag) => tag !== tagToRemove);
    onChange(id!, updatedList);
  };
  return (
    <InputContainer
      id={id}
      description={description}
      label={label}
      isRequired={isRequired}
      isInvalid={isInvalid}
      isDisabled={isDisabled}
      error={error}
    >
      <FormInput id={id} value={inputValue} onChange={handleInputChange} onKeyDown={handleAddTag} {...rest} />
      <HStack flexWrap="wrap" width="100%" spacing={2}>
        {value.map((label, index) => (
          <ListItem label={label} handleRemove={handleRemoveTag} key={index} />
        ))}
      </HStack>
    </InputContainer>
  );
}
