import React from 'react';
import {Box, Text, useInput} from 'ink';
import type {Portfolio, ETF, ETFSymbol} from '../types.js';
import {formatCurrency, formatPercent} from '../utils.js';
import {calculateTotalReturn} from '../portfolio-logic.js';

type ResultsScreenProps = {
	startingCash: number;
	portfolio: Portfolio;
	etfs: Record<ETFSymbol, ETF>;
	onContinue: () => void;
};

export function ResultsScreen({
	startingCash,
	portfolio,
	etfs,
	onContinue,
}: ResultsScreenProps) {
	useInput((input, key) => {
		if (key.return || input === ' ') {
			onContinue();
		}
	});

	const totalReturn = calculateTotalReturn(startingCash, portfolio.cash);
	const isNice = Math.abs(portfolio.cash - 10_420.69) < 1;

	return (
		<Box flexDirection="column" padding={1}>
			<Box marginBottom={1}>
				<Text bold color="cyan">
					=== After 1 Year of "Investing" ===
				</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1}>
				<Text>
					Starting: {formatCurrency(startingCash)}
				</Text>
				<Text>
					Ending:{' '}
					<Text color={portfolio.cash > startingCash ? 'green' : 'red'} bold>
						{formatCurrency(portfolio.cash)}
						{isNice ? ' (nice)' : ''}
					</Text>
				</Text>
				<Text>
					Total Return:{' '}
					<Text color={totalReturn > 0 ? 'green' : 'red'} bold>
						{formatPercent(totalReturn)}
					</Text>
				</Text>
			</Box>

			<Box marginBottom={1}>
				<Text>[CASH REGISTER NOISE]</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1}>
				<Text bold color="yellow">
					Performance by ETF:
				</Text>
				{(Object.keys(etfs) as ETFSymbol[]).map(symbol => {
					const etf = etfs[symbol]!;
					const allocation = portfolio.targetAllocation[symbol]! * 100;

					if (allocation < 0.1) return null;

					const commentary =
						etf.currentReturn > 0.1
							? '"TO THE MOON!"'
							: etf.currentReturn > 0
								? '"Slow and steady!"'
								: etf.currentReturn > -0.1
									? '"Could be worse..."'
									: '"Ouch."';

					return (
						<Box key={symbol}>
							<Box width={25}>
								<Text>{etf.sillyName}</Text>
							</Box>
							<Text>
								{etf.mood} {formatPercent(etf.currentReturn)}
							</Text>
							<Text color="gray"> {commentary}</Text>
						</Box>
					);
				})}
			</Box>

			<Box marginBottom={1}>
				<Text color="gray">Advisor says: "You could have just bought SPY"</Text>
			</Box>

			<Box>
				<Text color="green">Press Enter to see rebalancing options...</Text>
			</Box>
		</Box>
	);
}