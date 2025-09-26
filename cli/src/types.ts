export type ETFSymbol = 'VTI' | 'BND' | 'VXUS' | 'GOLD' | 'CRYPTO';

export type Mood = '😊' | '😐' | '😰' | '🤬';

export type RiskProfile = {
	name: string;
	description: string;
	equityPercent: number;
	emoji: string;
};

export type ETF = {
	symbol: ETFSymbol;
	sillyName: string;
	baseReturn: number;
	volatility: number;
	mood: Mood;
	currentReturn: number;
};

export type Portfolio = {
	cash: number;
	holdings: Record<ETFSymbol, number>;
	targetAllocation: Record<ETFSymbol, number>;
	currentAllocation: Record<ETFSymbol, number>;
};

export type MarketEvent = {
	name: string;
	description: string;
	impact: Partial<Record<ETFSymbol, number>>;
	emoji: string;
};

export type GameState = {
	screen: Screen;
	riskProfile: RiskProfile | null;
	portfolio: Portfolio;
	etfs: Record<ETFSymbol, ETF>;
	events: MarketEvent[];
	startingCash: number;
	currentDay: number;
	totalDays: number;
	diamondHands: boolean;
	simulationComplete: boolean;
};

export type Screen =
	| 'WELCOME'
	| 'RISK_SELECTION'
	| 'PORTFOLIO_DISPLAY'
	| 'SIMULATING'
	| 'RESULTS'
	| 'REBALANCE_PROMPT'
	| 'REBALANCE_DISPLAY'
	| 'DISCLAIMER';

export const RISK_PROFILES: RiskProfile[] = [
	{
		name: 'I keep money under my mattress',
		description: 'Ultra-conservative',
		equityPercent: 10,
		emoji: '🛏️',
	},
	{
		name: 'Dave Ramsey is my hero',
		description: 'Conservative',
		equityPercent: 30,
		emoji: '📻',
	},
	{
		name: 'Perfectly balanced, as all things should be',
		description: 'Moderate',
		equityPercent: 50,
		emoji: '⚖️',
	},
	{
		name: 'I eat volatility for breakfast',
		description: 'Aggressive',
		equityPercent: 70,
		emoji: '🍳',
	},
	{
		name: 'YOLO TO THE MOON 🚀',
		description: 'Very Aggressive',
		equityPercent: 90,
		emoji: '🚀',
	},
	{
		name: 'I bought GME at $400',
		description: 'Maximum Risk',
		equityPercent: 100,
		emoji: '💎',
	},
];

export const INITIAL_ETF_DATA: Record<ETFSymbol, Omit<ETF, 'mood' | 'currentReturn'>> = {
	VTI: {
		symbol: 'VTI',
		sillyName: 'YOLO Total Market ETF',
		baseReturn: 0.08,
		volatility: 0.15,
	},
	BND: {
		symbol: 'BND',
		sillyName: 'Boomer Bonds ETF',
		baseReturn: 0.02,
		volatility: 0.03,
	},
	VXUS: {
		symbol: 'VXUS',
		sillyName: 'Foreign Mystery ETF',
		baseReturn: 0.06,
		volatility: 0.18,
	},
	GOLD: {
		symbol: 'GOLD',
		sillyName: 'Shiny Rock ETF',
		baseReturn: 0.03,
		volatility: 0.12,
	},
	CRYPTO: {
		symbol: 'CRYPTO',
		sillyName: 'Magic Internet Money ETF',
		baseReturn: 0.15,
		volatility: 0.50,
	},
};