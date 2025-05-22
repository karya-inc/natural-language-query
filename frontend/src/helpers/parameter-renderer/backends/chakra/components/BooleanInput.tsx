import { ColorMap } from 'src/themes/Attributes';
import { SwitchProps } from '../../../types/InputComponentProps';
import { Checkbox, FormControl, Text, VStack } from '@chakra-ui/react';

export function BooleanInput(props: SwitchProps) {
  const { id, label, isInvalid, isDisabled, size: _size, className, ...rest } = props;
  return (
    <FormControl id={id} label={label} isInvalid={isInvalid} isDisabled={isDisabled} className={className}>
      {/**@ts-expect-error*/}
      <Checkbox id={id} {...rest} borderColor={ColorMap.white} alignItems={'flex-start'}>
        <VStack alignItems={'flex-start'} mt={'-6px'} spacing={'3px'}>
          <Text fontWeight={'medium'}>{label}</Text>
          {rest.description && (
            <Text color={ColorMap.stockGray} fontSize="sm">
              {rest.description}
            </Text>
          )}
        </VStack>
      </Checkbox>
    </FormControl>
  );
}
