import { Button, Text, Wrap, WrapItem } from '@chakra-ui/react';
import { ColorMap } from 'src/themes/Attributes';
import { ButtonVariant } from 'src/themes/ButtonVariants';

type ButtonSelectProps<T extends object> = {
  options: T;
  value: keyof T | '';
  onChange: (value: string) => void;
  isDisabled?: boolean;
};
export function ButtonSelect<T extends object>(props: ButtonSelectProps<T>) {
  const handleClick = (value: string) => {
    if (props.value === value) {
      props.onChange('');
    } else {
      props.onChange(value);
    }
  };
  const optionsEntries = Object.entries(props.options);
  if (optionsEntries.length === 0) {
    return (
      <Text color={ColorMap.stockGray} fontWeight="normal">
        No options available
      </Text>
    );
  }
  return (
    <Wrap gap="10px" justify="flex-start">
      {optionsEntries.map(([value, desc]) => {
        const isSelected = value === props.value;
        return (
          <WrapItem key={value} mr="5px">
            <Button
              variant={isSelected ? ButtonVariant.secondary_light : ButtonVariant.secondary_outlined_light}
              onClick={() => handleClick(value)}
              isDisabled={props.isDisabled}
            >
              {desc}
            </Button>
          </WrapItem>
        );
      })}
    </Wrap>
  );
}
