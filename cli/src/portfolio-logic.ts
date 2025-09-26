import type {
	ETF,
	ETFSymbol,
	Portfolio,
	RiskProfile,
	MarketEvent,
} from './types.js';
import {INITIAL_ETF_DATA} from './types.js';
import {gaussianRandom, getMoodFromReturn} from './utils.js';

export function createInitialPortfolio(
	riskProfile: RiskProfile,
	startingCash: number,
): Portfolio {
	const targetAllocation: Record<ETFSymbol, number> = {
		VTI: 0,
		BND: 0,
		VXUS: 0,
		GOLD: 0,
		CRYPTO: 0,
	};

	const equityPercent = riskProfile.equityPercent / 100;
	const bondsPercent = 1 - equityPercent;

	targetAllocation.VTI = equityPercent * 0.6;
	targetAllocation.VXUS = equityPercent * 0.3;
	targetAllocation.GOLD = equityPercent * 0.05;
	targetAllocation.CRYPTO = equityPercent * 0.05;
	targetAllocation.BND = bondsPercent;

	const holdings: Record<ETFSymbol, number> = {
		VTI: targetAllocation.VTI * startingCash,
		BND: targetAllocation.BND * startingCash,
		VXUS: targetAllocation.VXUS * startingCash,
		GOLD: targetAllocation.GOLD * startingCash,
		CRYPTO: targetAllocation.CRYPTO * startingCash,
	};

	return {
		cash: startingCash,
		holdings,
		targetAllocation,
		currentAllocation: {...targetAllocation},
	};
}

export function initializeETFs(): Record<ETFSymbol, ETF> {
	const etfs: Record<ETFSymbol, ETF> = {} as Record<ETFSymbol, ETF>;

	for (const [symbol, data] of Object.entries(INITIAL_ETF_DATA)) {
		etfs[symbol as ETFSymbol] = {
			...data,
			mood: '😐',
			currentReturn: 0,
		};
	}

	return etfs;
}

export function simulateOneDay(
	etfs: Record<ETFSymbol, ETF>,
	portfolio: Portfolio,
	event: MarketEvent | null,
	diamondHands: boolean,
): {etfs: Record<ETFSymbol, ETF>; portfolio: Portfolio} {
	const newETFs = {...etfs};
	const newHoldings = {...portfolio.holdings};

	for (const symbol of Object.keys(newETFs) as ETFSymbol[]) {
		const etf = newETFs[symbol]!;

		const dailyReturn =
			gaussianRandom(
				etf.baseReturn / 252,
				etf.volatility / Math.sqrt(252),
			) +
			(event?.impact[symbol] || 0);

		const finalReturn = diamondHands && dailyReturn < 0 ? 0 : dailyReturn;

		newETFs[symbol] = {
			...etf,
			currentReturn: etf.currentReturn + finalReturn,
			mood: getMoodFromReturn(etf.currentReturn + finalReturn),
		};

		newHoldings[symbol] = newHoldings[symbol]! * (1 + finalReturn);
	}

	const totalValue = Object.values(newHoldings).reduce(
		(sum, val) => sum + val,
		0,
	);
	const newCurrentAllocation: Record<ETFSymbol, number> = {} as Record<
		ETFSymbol,
		number
	>;

	for (const symbol of Object.keys(newHoldings) as ETFSymbol[]) {
		newCurrentAllocation[symbol] = newHoldings[symbol]! / totalValue;
	}

	return {
		etfs: newETFs,
		portfolio: {
			...portfolio,
			holdings: newHoldings,
			currentAllocation: newCurrentAllocation,
			cash: totalValue,
		},
	};
}

export function calculateRebalanceTrades(portfolio: Portfolio): {
	symbol: ETFSymbol;
	action: 'BUY' | 'SELL';
	amount: number;
}[] {
	const trades: {symbol: ETFSymbol; action: 'BUY' | 'SELL'; amount: number}[] =
		[];

	for (const symbol of Object.keys(portfolio.holdings) as ETFSymbol[]) {
		const currentValue = portfolio.holdings[symbol]!;
		const targetValue = portfolio.targetAllocation[symbol]! * portfolio.cash;
		const difference = targetValue - currentValue;

		if (Math.abs(difference) > 0.01) {
			trades.push({
				symbol,
				action: difference > 0 ? 'BUY' : 'SELL',
				amount: Math.abs(difference),
			});
		}
	}

	return trades;
}

export function calculateTotalReturn(
	startingCash: number,
	endingCash: number,
): number {
	return (endingCash - startingCash) / startingCash;
}

export function getPortfolioValue(portfolio: Portfolio): number {
	return Object.values(portfolio.holdings).reduce((sum, val) => sum + val, 0);
}