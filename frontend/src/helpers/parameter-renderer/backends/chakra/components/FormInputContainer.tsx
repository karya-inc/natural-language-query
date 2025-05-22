import { InputProps } from '../../../types/InputComponentProps';
import { Box, FormControl, FormHelperText, FormLabel, Text } from '@chakra-ui/react';
import { ColorMap } from 'src/themes/Attributes';

export function InputContainer(props: InputProps) {
  const { id, label, description, error, isInvalid, isDisabled, isRequired, size: _size, children } = props;
  return (
    <FormControl isInvalid={isInvalid} isDisabled={isDisabled} isRequired={isRequired}>
      <FormLabel as={Text} htmlFor={id} fontWeight="medium">
        {label}
      </FormLabel>
      <Text color={ColorMap.stockGray} fontSize="sm" mt="-10px">
        {description}
      </Text>
      <Box width="100%" pt="5px">
        {children}
      </Box>
      <FormHelperText color="red">{error}</FormHelperText>
    </FormControl>
  );
}
