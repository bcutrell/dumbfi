import React, {useEffect} from 'react';
import {Box, Text, useInput} from 'ink';
import type {Portfolio, ETF, ETFSymbol, RiskProfile} from '../types.js';
import {createAsciiBar, getRiskLevel} from '../utils.js';

type PortfolioDisplayProps = {
	portfolio: Portfolio;
	etfs: Record<ETFSymbol, ETF>;
	riskProfile: RiskProfile;
	onContinue: () => void;
};

export function PortfolioDisplay({
	portfolio,
	etfs,
	riskProfile,
	onContinue,
}: PortfolioDisplayProps) {
	useInput((input, key) => {
		if (key.return || input === ' ') {
			onContinue();
		}
	});

	useEffect(() => {
		const timer = setTimeout(() => {
			onContinue();
		}, 5000);

		return () => clearTimeout(timer);
	}, [onContinue]);

	return (
		<Box flexDirection="column" padding={1}>
			<Box marginBottom={1}>
				<Text bold color="yellow">
					📊 Your "Optimal" Portfolio 📊
				</Text>
			</Box>

			<Box marginBottom={1}>
				<Text>
					Risk Profile: {riskProfile.emoji} {riskProfile.name}
				</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1}>
				{(Object.keys(portfolio.targetAllocation) as ETFSymbol[]).map(
					symbol => {
						const allocation = portfolio.targetAllocation[symbol]! * 100;
						const etf = etfs[symbol]!;

						if (allocation < 0.1) return null;

						return (
							<Box key={symbol} marginY={0}>
								<Box width={25}>
									<Text>{etf.sillyName}</Text>
								</Box>
								<Box width={22}>
									<Text>[{createAsciiBar(allocation)}]</Text>
								</Box>
								<Box width={8}>
									<Text bold>{allocation.toFixed(0)}%</Text>
								</Box>
								<Text>{etf.mood}</Text>
							</Box>
						);
					},
				)}
			</Box>

			<Box marginBottom={1}>
				<Text>
					Risk Level: <Text bold>{getRiskLevel(riskProfile.equityPercent)}</Text>
				</Text>
			</Box>

			<Box>
				<Text color="gray">Press Enter or wait to start simulation...</Text>
			</Box>
		</Box>
	);
}