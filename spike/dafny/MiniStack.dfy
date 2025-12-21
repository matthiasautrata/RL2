// MiniStack: Verified Stack VM Spike
// Purpose: Evaluate Dafny for RL2 kernel
// See: spike-ministack.md for specification

datatype Value =
  | VBool(b: bool)
  | VInt(i: int)

datatype Instr =
  | Push(v: Value)
  | Dup
  | Drop
  | Swap
  | Eq
  | Lte
  | And
  | Or
  | Not
  | IfElse(thn: seq<Instr>, els: seq<Instr>)

datatype Result<A> =
  | Ok(value: A)
  | Err(msg: string)
{
  predicate IsOk() { Ok? }
  predicate IsErr() { Err? }
}

datatype VM = VM(stack: seq<Value>, fuel: nat)

// ============================================================
// Step Function
// ============================================================

function Step(vm: VM, instr: Instr): Result<VM>
  requires vm.fuel > 0
  ensures StepDecreasesFuel(vm, instr, Step(vm, instr))
  ensures StepBoundsStack(vm, instr, Step(vm, instr))
{
  var fuel' := vm.fuel - 1;
  match instr
  case Push(v) =>
    Ok(VM([v] + vm.stack, fuel'))

  case Dup =>
    if |vm.stack| < 1 then
      Err("underflow: Dup requires 1 element")
    else
      Ok(VM([vm.stack[0]] + vm.stack, fuel'))

  case Drop =>
    if |vm.stack| < 1 then
      Err("underflow: Drop requires 1 element")
    else
      Ok(VM(vm.stack[1..], fuel'))

  case Swap =>
    if |vm.stack| < 2 then
      Err("underflow: Swap requires 2 elements")
    else
      Ok(VM([vm.stack[1], vm.stack[0]] + vm.stack[2..], fuel'))

  case Eq =>
    if |vm.stack| < 2 then
      Err("underflow: Eq requires 2 elements")
    else
      var a := vm.stack[0];
      var b := vm.stack[1];
      match (a, b)
      case (VBool(x), VBool(y)) =>
        Ok(VM([VBool(x == y)] + vm.stack[2..], fuel'))
      case (VInt(x), VInt(y)) =>
        Ok(VM([VBool(x == y)] + vm.stack[2..], fuel'))
      case _ =>
        Err("type: Eq requires same types")

  case Lte =>
    if |vm.stack| < 2 then
      Err("underflow: Lte requires 2 elements")
    else
      match (vm.stack[0], vm.stack[1])
      case (VInt(a), VInt(b)) =>
        Ok(VM([VBool(b <= a)] + vm.stack[2..], fuel'))
      case _ =>
        Err("type: Lte requires int int")

  case And =>
    if |vm.stack| < 2 then
      Err("underflow: And requires 2 elements")
    else
      match (vm.stack[0], vm.stack[1])
      case (VBool(a), VBool(b)) =>
        Ok(VM([VBool(a && b)] + vm.stack[2..], fuel'))
      case _ =>
        Err("type: And requires bool bool")

  case Or =>
    if |vm.stack| < 2 then
      Err("underflow: Or requires 2 elements")
    else
      match (vm.stack[0], vm.stack[1])
      case (VBool(a), VBool(b)) =>
        Ok(VM([VBool(a || b)] + vm.stack[2..], fuel'))
      case _ =>
        Err("type: Or requires bool bool")

  case Not =>
    if |vm.stack| < 1 then
      Err("underflow: Not requires 1 element")
    else
      match vm.stack[0]
      case VBool(a) =>
        Ok(VM([VBool(!a)] + vm.stack[1..], fuel'))
      case _ =>
        Err("type: Not requires bool")

  case IfElse(thn, els) =>
    if |vm.stack| < 1 then
      Err("underflow: IfElse requires 1 element")
    else
      match vm.stack[0]
      case VBool(cond) =>
        var vm' := VM(vm.stack[1..], fuel');
        if cond then Run(vm', thn) else Run(vm', els)
      case _ =>
        Err("type: IfElse requires bool")
}

// ============================================================
// Run Function
// ============================================================

function Run(vm: VM, program: seq<Instr>): Result<VM>
  decreases vm.fuel, |program|
{
  if |program| == 0 then
    Ok(vm)
  else if vm.fuel == 0 then
    Err("fuel exhausted")
  else
    var r := Step(vm, program[0]);
    match r
    case Err(e) => Err(e)
    case Ok(vm') => Run(vm', program[1..])
}

// ============================================================
// Property Predicates
// ============================================================

// P1: Termination - fuel decreases on every successful step
predicate StepDecreasesFuel(vm: VM, instr: Instr, result: Result<VM>)
{
  result.Ok? ==> result.value.fuel < vm.fuel
}

// P3: Stack bounds - stack grows by at most 1 per instruction
predicate StepBoundsStack(vm: VM, instr: Instr, result: Result<VM>)
{
  result.Ok? ==> |result.value.stack| <= |vm.stack| + 1
}

// ============================================================
// Lemmas (Property Proofs)
// ============================================================

// P1: Every step decreases fuel
lemma TerminationLemma(vm: VM, instr: Instr)
  requires vm.fuel > 0
  ensures var r := Step(vm, instr); r.Ok? ==> r.value.fuel < vm.fuel
{
  // Proof is automatic from ensures clause on Step
}

// P3: Stack bounds
lemma StackBoundsLemma(vm: VM, instr: Instr)
  requires vm.fuel > 0
  ensures var r := Step(vm, instr); r.Ok? ==> |r.value.stack| <= |vm.stack| + 1
{
  // Proof is automatic from ensures clause on Step
}

// P5: Zero fuel always fails
lemma FuelExhaustionLemma(vm: VM, program: seq<Instr>)
  requires vm.fuel == 0
  requires |program| > 0
  ensures Run(vm, program).Err?
  ensures Run(vm, program).msg == "fuel exhausted"
{
  // Direct from Run definition
}

// ============================================================
// Test Cases
// ============================================================

method TestT1_BasicComparison()
{
  var program := [Push(VInt(3)), Push(VInt(5)), Lte];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VBool(true)];
  assert result.value.fuel == 7;
}

method TestT2_BooleanLogic()
{
  var program := [Push(VBool(true)), Push(VBool(false)), And];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VBool(false)];
}

method TestT3_StackManipulation()
{
  var program := [Push(VInt(1)), Push(VInt(2)), Swap, Drop];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VInt(2)];
}

method TestT4_Conditional()
{
  var program := [Push(VBool(true)), IfElse([Push(VInt(1))], [Push(VInt(2))])];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VInt(1)];
}

method TestT5_TypeError()
{
  var program := [Push(VInt(1)), Push(VBool(true)), And];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Err?;
  assert result.msg == "type: And requires bool bool";
}

method TestT6_Underflow()
{
  var program := [Drop];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Err?;
  assert result.msg == "underflow: Drop requires 1 element";
}

method TestT7_FuelExhaustion()
{
  var program := [Push(VInt(1)), Push(VInt(2)), Push(VInt(3))];
  var vm := VM([], 2);
  var result := Run(vm, program);
  assert result.Err?;
  assert result.msg == "fuel exhausted";
}

method TestT8_EqualitySameType()
{
  var program := [Push(VInt(5)), Push(VInt(5)), Eq];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VBool(true)];
}

method TestT9_EqualityDifferentTypes()
{
  var program := [Push(VInt(1)), Push(VBool(true)), Eq];
  var vm := VM([], 10);
  var result := Run(vm, program);
  assert result.Err?;
  assert result.msg == "type: Eq requires same types";
}

method TestT10_CompoundExpression()
{
  // (3 <= 5) AND (NOT false)
  var program := [
    Push(VInt(3)),
    Push(VInt(5)),
    Lte,
    Push(VBool(false)),
    Not,
    And
  ];
  var vm := VM([], 20);
  var result := Run(vm, program);
  assert result.Ok?;
  assert result.value.stack == [VBool(true)];
  assert result.value.fuel == 14;
}

// ============================================================
// Main (for extracted code testing)
// ============================================================

method Main()
{
  print "Running MiniStack tests...\n";
  TestT1_BasicComparison();
  TestT2_BooleanLogic();
  TestT3_StackManipulation();
  TestT4_Conditional();
  TestT5_TypeError();
  TestT6_Underflow();
  TestT7_FuelExhaustion();
  TestT8_EqualitySameType();
  TestT9_EqualityDifferentTypes();
  TestT10_CompoundExpression();
  print "All tests passed!\n";
}
