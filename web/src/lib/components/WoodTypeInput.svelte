<!-- WoodTypeInput.svelte -->
<script lang="ts">
	import type { WoodType } from '../../lib/types/wood';

	const props = $props();

	let newTypeName = $state<string | undefined>(undefined);
	let newTypeLength = $state<number | undefined>(undefined);
	let newTypePrice = $state<number | undefined>(undefined);

	function addWoodType(e: Event) {
		e.preventDefault();
		if (newTypeName && newTypeLength > 0 && newTypePrice > 0) {
			props.onUpdate({
				...props.woodTypes,
				[newTypeName]: {
					unit_length: newTypeLength,
					price: newTypePrice
				}
			});
			// Reset form
			newTypeName = undefined;
			newTypeLength = undefined;
			newTypePrice = undefined;
		}
	}

	function removeWoodType(typeName: string) {
		const { [typeName]: removed, ...rest } = props.woodTypes;
		props.onUpdate(rest);
	}
</script>

<div class="wood-types-container">
	<h2>Wood Types</h2>

	<!-- Existing Wood Types -->
	<div class="wood-types-list">
		{#each Object.entries(props.woodTypes || {}) as [typeName, type]}
			{@const woodType = type as WoodType}
			<div class="wood-type-item">
				<span class="type-name">{typeName}</span>
				<span class="type-details">
					Length: {woodType.unit_length}cm | Price: {woodType.price}
					{props.currency || 'USD'}
				</span>
				<button class="remove-btn" onclick={() => removeWoodType(typeName)}> Remove </button>
			</div>
		{/each}
	</div>

	<!-- Add New Wood Type Form -->
	<form 
		class="add-wood-type-form" 
		onsubmit={(e) => { 
			e.preventDefault();
			addWoodType(e);
		}}
	>
		<div class="form-row">
			<input
				type="text"
				bind:value={newTypeName}
				placeholder="Type name (e.g. pine 5x10)"
				required
			/>
			<input
				type="number"
				bind:value={newTypeLength}
				placeholder="Unit length (cm)"
				min="1"
				step="any"
				required
			/>
			<input
				type="number"
				bind:value={newTypePrice}
				placeholder="Price per unit ({props.currency || 'USD'})"
				min="0.01"
				step="any"
				required
			/>
			<button type="submit">Add Wood Type</button>
		</div>
	</form>
</div>

<style>
	.wood-types-container {
		padding: 1rem;
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	h2 {
		margin-bottom: 1rem;
		color: #2c3e50;
	}

	.wood-types-list {
		margin-bottom: 1.5rem;
	}

	.wood-type-item {
		display: flex;
		align-items: center;
		padding: 0.75rem;
		margin-bottom: 0.5rem;
		background: #f8f9fa;
		border-radius: 4px;
		gap: 1rem;
	}

	.type-name {
		font-weight: bold;
		min-width: 120px;
	}

	.type-details {
		flex-grow: 1;
		color: #666;
	}

	.remove-btn {
		padding: 0.25rem 0.75rem;
		background: #dc3545;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	.remove-btn:hover {
		background: #c82333;
	}

	.add-wood-type-form {
		background: #f8f9fa;
		padding: 1rem;
		border-radius: 4px;
	}

	.form-row {
		display: flex;
		gap: 1rem;
		align-items: center;
	}

	input {
		padding: 0.5rem;
		border: 1px solid #ced4da;
		border-radius: 4px;
		font-size: 1rem;
	}

	input[type='text'] {
		flex: 2;
	}

	input[type='number'] {
		flex: 1;
	}

	button[type='submit'] {
		padding: 0.5rem 1rem;
		background: #28a745;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	button[type='submit']:hover {
		background: #218838;
	}
</style>
