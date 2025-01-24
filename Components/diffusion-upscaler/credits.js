function computeCost(context) {
  // =FLOOR((((T10/T9)^2)/8)+2+(T10/1000),1)
  // const { steps, output_size, tile_size } = context;
  // const stepsCost = 1 + steps - 20 < 0 ? 1 : 1 + (steps - 20) * 0.1;
  // return { cost: stepsCost };
  return { cost: 1 };
  // 
}
