import { SectionContainerProps } from '../../../types/InputComponentProps';
import { SimpleGrid, Text, VStack } from '@chakra-ui/react';

export function SectionContainer(props: SectionContainerProps) {
  const { label, description, children } = props;
  return (
    <VStack alignItems="flex-start" marginBottom="10px">
      <Text fontSize="lg" fontWeight={600}>
        {label}
      </Text>
      <Text fontSize="sm">{description}</Text>
      <SimpleGrid columns={{ sm: 1 }} spacing={15} alignSelf="stretch" justifyContent="start">
        {children}
      </SimpleGrid>
    </VStack>
  );
}
