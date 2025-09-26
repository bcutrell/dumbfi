import React, {useState, useEffect, useCallback} from 'react';
import {Box, useApp} from 'ink';
import type {GameState, RiskProfile, Screen} from './types.js';
import {
	createInitialPortfolio,
	initializeETFs,
	simulateOneDay,
} from './portfolio-logic.js';
import {generateRandomEvent} from './events.js';
import {saveState, clearState} from './state-manager.js';
import {WelcomeScreen} from './components/WelcomeScreen.js';
import {RiskSelection} from './components/RiskSelection.js';
import {PortfolioDisplay} from './components/PortfolioDisplay.js';
import {SimulationScreen} from './components/SimulationScreen.js';
import {ResultsScreen} from './components/ResultsScreen.js';
import {RebalanceScreen} from './components/RebalanceScreen.js';
import {DisclaimerScreen} from './components/DisclaimerScreen.js';

const STARTING_CASH = 10_000;
const TOTAL_DAYS = 252;

export default function App() {
	const {exit} = useApp();
	const [gameState, setGameState] = useState<GameState>({
		screen: 'WELCOME',
		riskProfile: null,
		portfolio: {
			cash: STARTING_CASH,
			holdings: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
			targetAllocation: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
			currentAllocation: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
		},
		etfs: initializeETFs(),
		events: [],
		startingCash: STARTING_CASH,
		currentDay: 0,
		totalDays: TOTAL_DAYS,
		diamondHands: false,
		simulationComplete: false,
	});

	const setScreen = useCallback((screen: Screen) => {
		setGameState(previous => ({...previous, screen}));
	}, []);

	const handleRiskSelection = useCallback(
		(profile: RiskProfile, diamondHands: boolean) => {
			const portfolio = createInitialPortfolio(profile, STARTING_CASH);
			setGameState(previous => ({
				...previous,
				riskProfile: profile,
				portfolio,
				diamondHands,
				screen: 'PORTFOLIO_DISPLAY',
			}));
		},
		[],
	);

	const handleStartSimulation = useCallback(() => {
		setGameState(previous => ({
			...previous,
			screen: 'SIMULATING',
			currentDay: 0,
			simulationComplete: false,
		}));
	}, []);

	useEffect(() => {
		if (gameState.screen !== 'SIMULATING' || gameState.simulationComplete) {
			return;
		}

		const timer = setInterval(() => {
			setGameState(previous => {
				if (previous.currentDay >= previous.totalDays) {
					return {
						...previous,
						simulationComplete: true,
						screen: 'RESULTS',
					};
				}

				const event = generateRandomEvent(previous.currentDay);
				const {etfs, portfolio} = simulateOneDay(
					previous.etfs,
					previous.portfolio,
					event,
					previous.diamondHands,
				);

				const newEvents = event ? [...previous.events, event] : previous.events;

				return {
					...previous,
					etfs,
					portfolio,
					events: newEvents,
					currentDay: previous.currentDay + 1,
				};
			});
		}, 50);

		return () => clearInterval(timer);
	}, [gameState.screen, gameState.simulationComplete]);

	const handleViewRebalance = useCallback(() => {
		setScreen('REBALANCE_DISPLAY');
	}, [setScreen]);

	const handleShowDisclaimer = useCallback(() => {
		setScreen('DISCLAIMER');
	}, [setScreen]);

	const handlePlayAgain = useCallback(() => {
		clearState();
		setGameState({
			screen: 'WELCOME',
			riskProfile: null,
			portfolio: {
				cash: STARTING_CASH,
				holdings: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
				targetAllocation: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
				currentAllocation: {VTI: 0, BND: 0, VXUS: 0, GOLD: 0, CRYPTO: 0},
			},
			etfs: initializeETFs(),
			events: [],
			startingCash: STARTING_CASH,
			currentDay: 0,
			totalDays: TOTAL_DAYS,
			diamondHands: false,
			simulationComplete: false,
		});
	}, []);

	useEffect(() => {
		if (gameState.screen !== 'WELCOME') {
			saveState(gameState);
		}
	}, [gameState]);

	return (
		<Box>
			{gameState.screen === 'WELCOME' && (
				<WelcomeScreen onContinue={() => setScreen('RISK_SELECTION')} />
			)}

			{gameState.screen === 'RISK_SELECTION' && (
				<RiskSelection onSelect={handleRiskSelection} />
			)}

			{gameState.screen === 'PORTFOLIO_DISPLAY' &&
				gameState.riskProfile && (
					<PortfolioDisplay
						portfolio={gameState.portfolio}
						etfs={gameState.etfs}
						riskProfile={gameState.riskProfile}
						onContinue={handleStartSimulation}
					/>
				)}

			{gameState.screen === 'SIMULATING' && (
				<SimulationScreen
					currentDay={gameState.currentDay}
					totalDays={gameState.totalDays}
					currentEvent={
						gameState.events[gameState.events.length - 1] || null
					}
				/>
			)}

			{gameState.screen === 'RESULTS' && (
				<ResultsScreen
					startingCash={gameState.startingCash}
					portfolio={gameState.portfolio}
					etfs={gameState.etfs}
					onContinue={handleViewRebalance}
				/>
			)}

			{gameState.screen === 'REBALANCE_DISPLAY' && (
				<RebalanceScreen
					portfolio={gameState.portfolio}
					etfs={gameState.etfs}
					onContinue={handleShowDisclaimer}
				/>
			)}

			{gameState.screen === 'DISCLAIMER' && (
				<DisclaimerScreen onPlayAgain={handlePlayAgain} onExit={exit} />
			)}
		</Box>
	);
}