import { Box } from "@chakra-ui/react";
import { BOT_NAME } from "../config";

export function BotName() {
  return (
    <Box
      as="span"
      fontWeight="extrabold"
      bgGradient="linear(to-br, impactGreen, #C8E56E)"
      bgClip="text"
    >
      {BOT_NAME}
    </Box>
  );
}
