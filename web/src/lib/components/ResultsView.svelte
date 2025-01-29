<script lang="ts">
	import type { CalculationResult } from '../../lib/types/wood';

	interface Props {
		result: CalculationResult;
		currency: string;
	}

	const { result, currency = 'ILS' } = $props<Props>();

	// Debug logging
	console.log('Result data:', {
		result,
		costs: result.costs,
		arrangements: result.arrangements
	});

	let selectedType = $state<string | null>(null);

	// Calculate total cost directly
	const costs = Object.values(result.costs ?? {});
	console.log('Costs array:', costs);
	const totalCostValue = costs.reduce((sum, cost) => sum + (cost ?? 0), 0);
	console.log('Total cost calculated:', totalCostValue);

	const wastePercentage = $derived(
		typeof result.waste_statistics?.waste_percentage === 'number' 
			? result.waste_statistics.waste_percentage.toFixed(1) 
			: '0.0'
	);

	function formatCurrency(amount: number): string {
		console.log('Formatting amount:', amount);
		try {
			const cleanCurrency = currency.trim();
			const validAmount = typeof amount === 'number' && !isNaN(amount) ? amount : 0;
			console.log('Valid amount:', validAmount);
			return new Intl.NumberFormat('he-IL', {
				style: 'currency',
				currency: cleanCurrency,
				minimumFractionDigits: 2,
				maximumFractionDigits: 2
			}).format(validAmount);
		} catch (error) {
			console.error('Currency formatting error:', error);
			const validAmount = typeof amount === 'number' && !isNaN(amount) ? amount : 0;
			return `${validAmount.toFixed(2)} ${currency.trim()}`;
		}
	}

	function getTypeCost(woodType: string): number {
		console.log('Getting cost for type:', woodType, result.costs?.[woodType]);
		return result.costs?.[woodType] ?? 0;
	}

	function toggleType(type: string) {
		selectedType = selectedType === type ? null : type;
	}
</script>

<div class="results-container">
	<h2>Calculation Results</h2>

	<!-- Summary Section -->
	<div class="summary-section">
		<div class="summary-card">
			<h3>Total Cost</h3>
			<div class="value">{formatCurrency(totalCostValue)}</div>
		</div>
		<div class="summary-card">
			<h3>Waste Percentage</h3>
			<div class="value">{wastePercentage}%</div>
		</div>
		<div class="summary-card">
			<h3>Total Wood Types</h3>
			<div class="value">{result.arrangements.length}</div>
		</div>
	</div>

	<!-- Wood Types List -->
	<div class="wood-types-section">
		<h3>Wood Types Breakdown</h3>
		<div class="wood-types-list">
			{#each result.arrangements as arrangement}
				<div
					class="wood-type-card"
					class:active={selectedType === arrangement.wood_type}
					onclick={() => toggleType(arrangement.wood_type)}
					onkeydown={(e) => e.key === 'Enter' && toggleType(arrangement.wood_type)}
					role="button"
					tabindex="0"
				>
					<div class="wood-type-header">
						<h4>{arrangement.wood_type}</h4>
						<span class="units-count">
							{result.total_units?.[arrangement.wood_type] ?? 0} units
						</span>
					</div>
					<div class="wood-type-cost">
						{formatCurrency(getTypeCost(arrangement.wood_type))}
					</div>
					<div class="expand-hint">
						Click to {selectedType === arrangement.wood_type ? 'hide' : 'show'} details
					</div>
				</div>

				{#if selectedType === arrangement.wood_type}
					<div class="arrangement-details">
						{#each arrangement.units as unit}
							<div class="unit-card">
								<h5>Unit {unit.unit_number}</h5>
								<div class="pieces-list">
									{#each Object.entries(unit.pieces ?? {}) as [length, count]}
										<div class="piece-item">
											{count}x {length}cm
										</div>
									{/each}
								</div>
								<div class="waste-info">
									Waste: {(unit.waste ?? 0).toFixed(1)}cm
								</div>
							</div>
						{/each}
					</div>
				{/if}
			{/each}
		</div>
	</div>
</div>

<style>
	.results-container {
		padding: 1rem;
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	h2,
	h3,
	h4,
	h5 {
		color: #2c3e50;
		margin: 0 0 1rem 0;
	}

	.summary-section {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.summary-card {
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 8px;
		text-align: center;
	}

	.summary-card h3 {
		font-size: 1rem;
		margin-bottom: 0.5rem;
	}

	.value {
		font-size: 1.5rem;
		font-weight: bold;
		color: #3498db;
	}

	.wood-types-section {
		margin-top: 2rem;
	}

	.wood-types-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.wood-type-card {
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.wood-type-card:hover {
		background: #e9ecef;
	}

	.wood-type-card.active {
		background: #e3f2fd;
		border-bottom-left-radius: 0;
		border-bottom-right-radius: 0;
	}

	.wood-type-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.wood-type-header h4 {
		margin: 0;
	}

	.units-count {
		color: #6c757d;
		font-size: 0.9rem;
	}

	.wood-type-cost {
		font-size: 1.2rem;
		font-weight: bold;
		color: #28a745;
		margin-bottom: 0.5rem;
	}

	.expand-hint {
		font-size: 0.8rem;
		color: #6c757d;
	}

	.arrangement-details {
		padding: 1rem;
		background: #fff;
		border: 1px solid #e3f2fd;
		border-top: none;
		border-bottom-left-radius: 8px;
		border-bottom-right-radius: 8px;
		margin-top: -1rem;
	}

	.unit-card {
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 4px;
		margin-bottom: 1rem;
	}

	.unit-card:last-child {
		margin-bottom: 0;
	}

	.unit-card h5 {
		margin-bottom: 0.5rem;
	}

	.pieces-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.piece-item {
		padding: 0.25rem 0.5rem;
		background: #e9ecef;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.waste-info {
		font-size: 0.9rem;
		color: #dc3545;
	}
</style>
