// Copyright (c) DAIA Tech Pvt Ltd
//
// Load one of karya's cloudfare images

import { Image, ImageProps } from "@chakra-ui/react";

const CFImageMap = {
  "karya-logo": "c734fc52-a5a4-4e05-d491-c4e7a5678200",
  "karya-logo-name-horizontal": "1ec3bea2-6c24-4388-66b1-f80038399500",
  "karya-logo-name-vertical": "2983f14c-3d91-4da5-faf3-c49095eb8500",
} as const;

type CFImageName = keyof typeof CFImageMap;

export default function CFImage(props: ImageProps & { cfsrc: CFImageName }) {
  const imageId = CFImageMap[props.cfsrc];
  return (
    <Image
      {...props}
      src={`https://imagedelivery.net/zZi_VLBckmtLzucvU2-pnQ/${imageId}/public`}
    />
  );
}
