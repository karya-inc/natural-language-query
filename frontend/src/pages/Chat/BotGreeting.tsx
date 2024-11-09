import { Image, Heading, Box, HStack } from "@chakra-ui/react";
import CFImage from "../../components/CloudflareImage";

const BOT_NAME = "Kalai";

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
    </HStack>
  );
};

export default BotGreeting;
