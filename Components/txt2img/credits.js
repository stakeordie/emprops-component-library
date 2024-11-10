function computeCredits(context) {
  const { steps, width, height } = context;
  return (steps - 20) * 0.01;
}