import { Flex, Image, Heading, Box } from "@chakra-ui/react";

const BOT_NAME = "Kalai";

const BotGreeting = () => {
  return (
    <Flex gap={2}>
      <Image src="karya-logo.svg" w="40px" h="40px" alt="Karya logo" />
      <Heading color="gray.500" fontWeight="normal">
        Hello, how can{" "}
        <Box
          as="span"
          fontWeight="extrabold"
          bgGradient="linear(to-br, impactGreen, #C8E56E)"
          bgClip="text"
        >
          {BOT_NAME}
        </Box>{" "}
        help you today?
      </Heading>
    </Flex>
  );
};

export default BotGreeting;
