import React from 'react';
import {Box, Text, useInput} from 'ink';
import type {Portfolio, ETF, ETFSymbol} from '../types.js';
import {formatCurrency, createAsciiBar} from '../utils.js';
import {calculateRebalanceTrades} from '../portfolio-logic.js';

type RebalanceScreenProps = {
	portfolio: Portfolio;
	etfs: Record<ETFSymbol, ETF>;
	onContinue: () => void;
};

export function RebalanceScreen({
	portfolio,
	etfs,
	onContinue,
}: RebalanceScreenProps) {
	useInput((input, key) => {
		if (key.return || input === ' ') {
			onContinue();
		}
	});

	const trades = calculateRebalanceTrades(portfolio);
	const taxImplication = 350;

	return (
		<Box flexDirection="column" padding={1}>
			<Box marginBottom={1}>
				<Text bold color="yellow">
					⚖️  Rebalancing Analysis ⚖️
				</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1}>
				<Text bold underline>
					Current vs Target Allocation:
				</Text>
				{(Object.keys(portfolio.holdings) as ETFSymbol[]).map(symbol => {
					const current = portfolio.currentAllocation[symbol]! * 100;
					const target = portfolio.targetAllocation[symbol]! * 100;
					const etf = etfs[symbol]!;

					if (target < 0.1) return null;

					const drift = Math.abs(current - target);
					const needsRebalance = drift > 1;

					return (
						<Box key={symbol} flexDirection="column" marginY={0}>
							<Box>
								<Box width={25}>
									<Text>{etf.sillyName}</Text>
								</Box>
							</Box>
							<Box>
								<Box width={10}>
									<Text color="gray">Current:</Text>
								</Box>
								<Box width={22}>
									<Text>[{createAsciiBar(current)}]</Text>
								</Box>
								<Text>
									{current.toFixed(1)}%{' '}
									{needsRebalance ? (
										<Text color="yellow">(drift: {drift.toFixed(1)}%)</Text>
									) : null}
								</Text>
							</Box>
							<Box>
								<Box width={10}>
									<Text color="gray">Target:</Text>
								</Box>
								<Box width={22}>
									<Text>[{createAsciiBar(target)}]</Text>
								</Box>
								<Text>{target.toFixed(1)}%</Text>
							</Box>
						</Box>
					);
				})}
			</Box>

			{trades.length > 0 ? (
				<>
					<Box flexDirection="column" marginBottom={1}>
						<Text bold underline>
							Required Trades:
						</Text>
						{trades.map((trade, index) => {
							const etf = etfs[trade.symbol]!;
							const isNice = Math.abs(trade.amount - 420.69) < 1;

							return (
								<Box key={index}>
									<Text
										color={trade.action === 'BUY' ? 'green' : 'red'}
										bold
									>
										{trade.action}
									</Text>
									<Text>
										{' '}
										{formatCurrency(trade.amount)}
										{isNice ? ' (nice)' : ''} of {etf.sillyName}
									</Text>
								</Box>
							);
						})}
					</Box>

					<Box marginBottom={1}>
						<Text>
							Tax Implications: <Text bold>{formatCurrency(taxImplication)}</Text>
						</Text>
					</Box>
				</>
			) : (
				<Box marginBottom={1}>
					<Text color="green">
						✅ Portfolio is perfectly balanced! No trades needed.
					</Text>
				</Box>
			)}

			<Box>
				<Text color="gray">Press Enter to continue...</Text>
			</Box>
		</Box>
	);
}