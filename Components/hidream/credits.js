function computeCost(context) {
  let cost = 3;
  if(context.model == 0) {
    cost = 3;
  } else if (context.model == 1) {
    cost = 5;
  } else {
    cost = 11;
  }
  return { cost };
}