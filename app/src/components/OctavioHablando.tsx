import { type ComponentProps, useEffect, useState } from 'react';
import { Animated } from 'react-native';

import { Octavio } from '@/components/Octavio';

type Props = ComponentProps<typeof Octavio> & { hablando: boolean };

// Octavio se mece mientras habla.
export function OctavioHablando({ hablando, ...octavio }: Props) {
  const [altura] = useState(() => new Animated.Value(0));
  useEffect(() => {
    if (!hablando) {
      Animated.spring(altura, { toValue: 0, useNativeDriver: true }).start();
      return;
    }
    const vaiven = Animated.loop(
      Animated.sequence([
        Animated.timing(altura, { toValue: -8, duration: 260, useNativeDriver: true }),
        Animated.timing(altura, { toValue: 0, duration: 260, useNativeDriver: true }),
      ]),
    );
    vaiven.start();
    return () => vaiven.stop();
  }, [altura, hablando]);
  return (
    <Animated.View style={{ transform: [{ translateY: altura }] }}>
      <Octavio {...octavio} />
    </Animated.View>
  );
}
