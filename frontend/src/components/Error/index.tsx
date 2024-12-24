import { HStack, Text } from "@chakra-ui/react";
import CFImage from "../CloudflareImage";

const Error = () => {
  return (
    <HStack
      bg="gray.900"
      align="center"
      justify="center"
      gap={6}
      w="100%"
      h="100vh"
      p={8}
      color="white"
    >
      <CFImage
        cfsrc="karya-logo"
        boxSize={10}
        border="1px solid"
        borderColor="gray.600"
        borderRadius={50}
        p={2}
      />
      <Text>Something went wrong. Please try again later.</Text>
    </HStack>
  );
};

export default Error;
