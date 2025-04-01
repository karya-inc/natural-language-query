import { Tag, TagCloseButton, TagLabel } from '@chakra-ui/react';

export interface ListItemProps {
  label: string;
  handleRemove: (label: string) => void;
}
export function ListItem(props: ListItemProps) {
  const { label, handleRemove } = props;
  return (
    <Tag colorScheme="whatsapp">
      <TagLabel>{label}</TagLabel>
      <TagCloseButton onClick={() => handleRemove(label)} tabIndex={-1} />
    </Tag>
  );
}
