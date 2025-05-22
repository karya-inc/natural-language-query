import { MultiFileInputProps } from '../../../types/InputComponentProps';
import { InputContainer } from './FormInputContainer';
import { Button, HStack, IconButton, Text, VStack } from '@chakra-ui/react';
import { RiCloseLine } from 'react-icons/ri';
import { useRef } from 'react';

export function MultiFileInput(props: MultiFileInputProps) {
  const {
    id,
    description,
    label,
    value,
    onChange,
    showFileNames,
    error,
    isInvalid,
    isDisabled,
    isRequired,
    size: _size,
    ...rest
  } = props;
  const inputRef = useRef<HTMLInputElement>(null);

  const handleBrowse = () => {
    inputRef.current?.click();
  };

  const handleInputChange = () => {
    const uploadedFiles = inputRef.current?.files;
    const uploadedFilesArray = uploadedFiles ? Array.from(uploadedFiles) : undefined;
    if (uploadedFilesArray) {
      const files = [...value, ...uploadedFilesArray];
      onChange(id!, files);
    }
  };
  const handleDelete = (file: File) => {
    if (file) {
      const files = value.filter((f) => f !== file);
      onChange(id!, files);
    }
  };
  const handleDeleteAll = () => {
    onChange(id!, []);
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
      <input id={id} type="file" ref={inputRef} onChange={handleInputChange} hidden {...rest} multiple />
      <VStack align="start">
        <Button variant="submit" isDisabled={isDisabled} onClick={handleBrowse} marginBottom={3}>
          Select File(s)
        </Button>
        {showFileNames === false ? (
          value.length !== 0 ? (
            <HStack marginTop="-6" marginStart={3}>
              <Text>{value.length} file(s) selected</Text>
              <IconButton
                aria-label="Delete all files"
                icon={<RiCloseLine />}
                onClick={() => handleDeleteAll()}
                style={{ background: 'none' }}
              />
            </HStack>
          ) : null
        ) : (
          value.map((file) => (
            <HStack marginTop="-6" marginStart={3}>
              <Text fontSize="small">{file && file.name}</Text>
              <IconButton
                aria-label="Delete file from list"
                icon={<RiCloseLine />}
                onClick={() => handleDelete(file)}
                style={{ background: 'none' }}
              />
            </HStack>
          ))
        )}
      </VStack>
    </InputContainer>
  );
}
