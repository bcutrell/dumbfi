import React, {useState} from 'react';
import {Box, Text, useInput} from 'ink';
import {RISK_PROFILES, type RiskProfile} from '../types.js';
import {checkEasterEgg} from '../utils.js';

type RiskSelectionProps = {
	onSelect: (profile: RiskProfile, diamondHands: boolean) => void;
};

export function RiskSelection({onSelect}: RiskSelectionProps) {
	const [selectedIndex, setSelectedIndex] = useState(0);
	const [easterEggInput, setEasterEggInput] = useState('');

	useInput((input, key) => {
		if (key.upArrow) {
			setSelectedIndex(previous =>
				previous > 0 ? previous - 1 : RISK_PROFILES.length - 1,
			);
		} else if (key.downArrow) {
			setSelectedIndex(previous =>
				previous < RISK_PROFILES.length - 1 ? previous + 1 : 0,
			);
		} else if (key.return) {
			const diamondHands = checkEasterEgg(easterEggInput);
			onSelect(RISK_PROFILES[selectedIndex]!, diamondHands);
		} else if (input) {
			setEasterEggInput(previous => previous + input);
		}
	});

	return (
		<Box flexDirection="column" padding={1}>
			<Box marginBottom={1}>
				<Text bold color="yellow">
					💰 How much risk can your heart handle? 💰
				</Text>
			</Box>

			<Box flexDirection="column">
				{RISK_PROFILES.map((profile, index) => (
					<Box key={profile.name} marginY={0}>
						<Text
							color={index === selectedIndex ? 'cyan' : 'white'}
							bold={index === selectedIndex}
						>
							{index === selectedIndex ? '→ ' : '  '}
							{profile.emoji} {profile.name} ({profile.equityPercent}% equity)
						</Text>
					</Box>
				))}
			</Box>

			<Box marginTop={2}>
				<Text color="gray">Use ↑/↓ arrows to select, Enter to confirm</Text>
			</Box>

			{checkEasterEgg(easterEggInput) && (
				<Box marginTop={1}>
					<Text color="green" bold>
						💎🙌 DIAMOND HANDS ACTIVATED! Losses are now illegal! 💎🙌
					</Text>
				</Box>
			)}
		</Box>
	);
}