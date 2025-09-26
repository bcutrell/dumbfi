import React, {useState, useEffect} from 'react';
import {Box, Text} from 'ink';
import Spinner from 'ink-spinner';
import type {MarketEvent} from '../types.js';
import {getRandomLoadingMessage} from '../utils.js';
import {generateEventDescription} from '../events.js';

type SimulationScreenProps = {
	currentDay: number;
	totalDays: number;
	currentEvent: MarketEvent | null;
};

export function SimulationScreen({
	currentDay,
	totalDays,
	currentEvent,
}: SimulationScreenProps) {
	const [loadingMessage] = useState(getRandomLoadingMessage());
	const progress = ((currentDay / totalDays) * 100).toFixed(0);
	const daysPerMonth = 21;
	const currentMonth = Math.floor(currentDay / daysPerMonth) + 1;

	const [recentEvents, setRecentEvents] = useState<MarketEvent[]>([]);

	useEffect(() => {
		if (currentEvent) {
			setRecentEvents(previous => [...previous.slice(-4), currentEvent]);
		}
	}, [currentEvent]);

	return (
		<Box flexDirection="column" padding={1}>
			<Box marginBottom={1}>
				<Text bold color="cyan">
					<Spinner type="dots" /> Simulating Year of "Investing"...
				</Text>
			</Box>

			<Box marginBottom={1}>
				<Text>{loadingMessage}</Text>
			</Box>

			<Box marginBottom={1}>
				<Text>
					Month {currentMonth} of 12 • Day {currentDay} of {totalDays} • {progress}%
					complete
				</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1}>
				<Text bold color="yellow">
					Recent Market Events:
				</Text>
				{recentEvents.length === 0 ? (
					<Text color="gray">Nothing happened yet...</Text>
				) : (
					recentEvents.map((event, index) => (
						<Box key={index} marginTop={0}>
							<Text color="white">{generateEventDescription(event)}</Text>
						</Box>
					))
				)}
			</Box>

			{currentEvent && (
				<Box>
					<Text color="cyan" bold>
						🎲 {currentEvent.name}
					</Text>
				</Box>
			)}
		</Box>
	);
}