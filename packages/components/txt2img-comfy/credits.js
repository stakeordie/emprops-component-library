function computeCost(context) {
  const { steps } = context;
  const stepsCost = 1 + steps - 20 < 0 ? 1 : 1 + (steps - 20) * 0.1;
  return { cost: stepsCost };
}
