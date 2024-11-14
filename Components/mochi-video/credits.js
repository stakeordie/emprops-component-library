function computeCost(context) {
  const time = context.length * 15;
  const credits = time / 10;
  return credits;
}
