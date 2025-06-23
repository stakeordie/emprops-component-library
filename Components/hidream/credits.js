function computeCost(context) {
  let cost = 1;
  if(context.model == 0) {
    cost = 1.5;
  } else if (context.model == 1) {
    cost = 2.5;
  } else {
    cost = 4;
  }
  return { cost };
}