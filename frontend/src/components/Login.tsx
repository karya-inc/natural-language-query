import { Button, Card, Center, Heading } from "@chakra-ui/react";
import { BotName } from "./RenderBotName";

export type LoginProps = {
  onLogin: () => void;
};
export function Login(props: LoginProps) {
  return (
    <Center height="100%" bg="gray.900">
      <Card width="400px" bg="gray.700" padding={8} gap={5}>
        <Heading
          color="whiteAlpha.800"
          fontWeight="bold"
          fontSize="2xl"
          textAlign="center"
        >
          Welcome to <BotName />
        </Heading>
        <Button
          bgGradient="linear(to-r, impactGreen, #A8E55E, impactGreen)"
          color="blackAlpha.800"
          onClick={props.onLogin}
          transition="all 0.4s ease-in-out"
          _hover={{
            backgroundPosition: "100% 0",
          }}
          backgroundSize="300% 300%"
        >
          Sign In
        </Button>
      </Card>
    </Center>
  );
}
