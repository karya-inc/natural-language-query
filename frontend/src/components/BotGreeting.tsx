import { Heading, HStack } from "@chakra-ui/react";
import CFImage from "./CloudflareImage";
import { BotName } from "./RenderBotName";

const BotGreeting = () => {
  return (
    <HStack
      w={{ base: "80vw", md: "50vw", lg: "70vw" }}
      align={{ base: "flex-start", lg: "center" }}
      gap={{ base: 4, xl: 2 }}
      justify="center"
    >
      <CFImage
        cfsrc="karya-logo"
        w={{ base: "30px", lg: "40px" }}
        h="30px"
        alt="Karya logo"
      />
      <Heading color="gray.500" fontWeight="normal">
        Hello, how can <BotName /> help you today?
      </Heading>
    </HStack>
  );
};

export default BotGreeting;
