function computeCost(context) {
  const outputSize = context.output_size; // T10
  const tileSize = context.tile_size; // T9
  const cost = Math.floor(
    Math.pow(outputSize / tileSize, 2) / 8 + 2 + outputSize / 1000
  );
  return { cost };
}
