<script lang="ts">
	import type { WoodPiece } from '../../lib/types/wood';
	import type { HTMLButtonAttributes, ClipboardEventHandler } from 'svelte/elements';

	type Props = {
		pieces: WoodPiece[];
		availableTypes: string[];
		onUpdate: (pieces: WoodPiece[]) => void;
		onReset: () => void;
	} & HTMLButtonAttributes;
	let { pieces, availableTypes, onUpdate, onReset } = $props();

	const newPiece = $state<WoodPiece>({
		type: '',
		length: undefined,
		count: undefined
	});

	function addPiece(e: SubmitEvent) {
		e.preventDefault();
		if (newPiece.type && newPiece.length > 0 && newPiece.count > 0) {
			onUpdate([...pieces, { ...newPiece }]);
			// Reset form except for type
			newPiece.length = undefined;
			newPiece.count = undefined;
		}
	}

	function removePiece(index: number) {
		onUpdate(pieces.filter((_, i) => i !== index));
	}

	function handlePaste(e: ClipboardEvent) {
		e.preventDefault();
		const text = e.clipboardData?.getData('text') || '';
		const rows = text.trim().split('\n');

		const newPieces = rows
			.map((row) => {
				const [type, length, count] = row.split('\t');
				return {
					type: type?.trim() || '',
					length: parseFloat(length?.trim() || '0'),
					count: parseInt(count?.trim() || '1', 10)
				};
			})
			.filter((p) => p.type && p.length > 0 && p.count > 0);

		if (newPieces.length > 0) {
			onUpdate([...pieces, ...newPieces]);
		}
	}
</script>

<div class="pieces-container">
	<div class="header">
		<h2>Required Pieces</h2>
		{#if pieces.length > 0}
			<button class="reset-btn" onclick={onReset}>Reset All</button>
		{/if}
	</div>

	<!-- Existing Pieces Table -->
	<div class="pieces-table">
		<table>
			<thead>
				<tr>
					<th>Wood Type</th>
					<th>Length (cm)</th>
					<th>Count</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody onpaste={handlePaste}>
				{#each pieces as piece, i}
					<tr>
						<td>{piece.type}</td>
						<td>{piece.length}</td>
						<td>{piece.count}</td>
						<td>
							<button class="remove-btn" onclick={(e) => removePiece(i)}> Remove </button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Add New Piece Form -->
	<form class="add-piece-form" onsubmit={addPiece}>
		<div class="form-row">
			<select bind:value={newPiece.type} required>
				<option value="">Select Wood Type</option>
				{#each availableTypes as type}
					<option value={type}>{type}</option>
				{/each}
			</select>
			<input
				type="number"
				bind:value={newPiece.length}
				placeholder="Length (cm)"
				min="1"
				step="any"
				required
			/>
			<input type="number" bind:value={newPiece.count} placeholder="Count" min="1" required />
			<button type="submit">Add Piece</button>
		</div>
	</form>

	<div class="paste-hint">
		<p>💡 Tip: You can paste data from a spreadsheet (Type ⇥ Length ⇥ Count)</p>
	</div>
</div>

<style>
	.pieces-container {
		padding: 1rem;
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	h2 {
		margin: 0;
		color: #2c3e50;
	}

	.reset-btn {
		padding: 0.5rem 1rem;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}

	.reset-btn:hover {
		background: #5a6268;
	}

	.pieces-table {
		margin-bottom: 1.5rem;
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin-bottom: 1rem;
	}

	th,
	td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid #dee2e6;
	}

	th {
		background: #f8f9fa;
		font-weight: bold;
		color: #2c3e50;
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

	.add-piece-form {
		background: #f8f9fa;
		padding: 1rem;
		border-radius: 4px;
		margin-bottom: 1rem;
	}

	.form-row {
		display: flex;
		gap: 1rem;
		align-items: center;
	}

	select,
	input {
		padding: 0.5rem;
		border: 1px solid #ced4da;
		border-radius: 4px;
		font-size: 1rem;
	}

	select {
		flex: 2;
	}

	input {
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

	.paste-hint {
		color: #6c757d;
		font-size: 0.9rem;
		text-align: center;
	}
</style>
