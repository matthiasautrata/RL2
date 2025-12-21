// MiniStack: Verified Stack VM Spike
// Purpose: Evaluate Stainless for RL2 kernel
// See: spike-ministack.md for specification

import stainless.lang._
import stainless.collection._
import stainless.annotation._

object MiniStack {

  // ============================================================
  // Values
  // ============================================================

  sealed abstract class Value
  case class VBool(b: Boolean) extends Value
  case class VInt(i: BigInt) extends Value

  // ============================================================
  // Instructions
  // ============================================================

  sealed abstract class Instr
  case class Push(v: Value) extends Instr
  case object Dup extends Instr
  case object Drop extends Instr
  case object Swap extends Instr
  case object Eq extends Instr
  case object Lte extends Instr
  case object And extends Instr
  case object Or extends Instr
  case object Not extends Instr
  case class IfElse(thn: List[Instr], els: List[Instr]) extends Instr

  // ============================================================
  // Result Type
  // ============================================================

  sealed abstract class Result[A]
  case class Ok[A](value: A) extends Result[A]
  case class Err[A](msg: String) extends Result[A]

  // ============================================================
  // VM State
  // ============================================================

  case class VM(stack: List[Value], fuel: BigInt) {
    require(fuel >= 0)
  }

  // ============================================================
  // Step Function
  // ============================================================

  def step(vm: VM, instr: Instr): Result[VM] = {
    require(vm.fuel > 0)

    val fuel1 = vm.fuel - 1

    instr match {
      case Push(v) =>
        Ok(VM(v :: vm.stack, fuel1))

      case Dup =>
        vm.stack match {
          case Nil() => Err("underflow: Dup requires 1 element")
          case Cons(a, _) => Ok(VM(a :: vm.stack, fuel1))
        }

      case Drop =>
        vm.stack match {
          case Nil() => Err("underflow: Drop requires 1 element")
          case Cons(_, rest) => Ok(VM(rest, fuel1))
        }

      case Swap =>
        vm.stack match {
          case Cons(a, Cons(b, rest)) => Ok(VM(b :: a :: rest, fuel1))
          case _ => Err("underflow: Swap requires 2 elements")
        }

      case Eq =>
        vm.stack match {
          case Cons(VBool(x), Cons(VBool(y), rest)) =>
            Ok(VM(VBool(x == y) :: rest, fuel1))
          case Cons(VInt(x), Cons(VInt(y), rest)) =>
            Ok(VM(VBool(x == y) :: rest, fuel1))
          case Cons(_, Cons(_, _)) =>
            Err("type: Eq requires same types")
          case _ =>
            Err("underflow: Eq requires 2 elements")
        }

      case Lte =>
        vm.stack match {
          case Cons(VInt(a), Cons(VInt(b), rest)) =>
            Ok(VM(VBool(b <= a) :: rest, fuel1))
          case Cons(_, Cons(_, _)) =>
            Err("type: Lte requires int int")
          case _ =>
            Err("underflow: Lte requires 2 elements")
        }

      case And =>
        vm.stack match {
          case Cons(VBool(a), Cons(VBool(b), rest)) =>
            Ok(VM(VBool(a && b) :: rest, fuel1))
          case Cons(_, Cons(_, _)) =>
            Err("type: And requires bool bool")
          case _ =>
            Err("underflow: And requires 2 elements")
        }

      case Or =>
        vm.stack match {
          case Cons(VBool(a), Cons(VBool(b), rest)) =>
            Ok(VM(VBool(a || b) :: rest, fuel1))
          case Cons(_, Cons(_, _)) =>
            Err("type: Or requires bool bool")
          case _ =>
            Err("underflow: Or requires 2 elements")
        }

      case Not =>
        vm.stack match {
          case Cons(VBool(a), rest) =>
            Ok(VM(VBool(!a) :: rest, fuel1))
          case Cons(_, _) =>
            Err("type: Not requires bool")
          case Nil() =>
            Err("underflow: Not requires 1 element")
        }

      case IfElse(thn, els) =>
        vm.stack match {
          case Cons(VBool(cond), rest) =>
            val vm1 = VM(rest, fuel1)
            if (cond) run(vm1, thn) else run(vm1, els)
          case Cons(_, _) =>
            Err("type: IfElse requires bool")
          case Nil() =>
            Err("underflow: IfElse requires 1 element")
        }
    }
  } ensuring { res =>
    // P1: Termination - fuel decreases
    res match {
      case Ok(vm1) => vm1.fuel < vm.fuel
      case Err(_) => true
    }
  }

  // ============================================================
  // Run Function
  // ============================================================

  def run(vm: VM, program: List[Instr]): Result[VM] = {
    decreases(vm.fuel, program.size)

    program match {
      case Nil() => Ok(vm)
      case Cons(i, rest) =>
        if (vm.fuel == 0) {
          Err("fuel exhausted")
        } else {
          step(vm, i) match {
            case Err(e) => Err(e)
            case Ok(vm1) => run(vm1, rest)
          }
        }
    }
  }

  // ============================================================
  // Property Lemmas
  // ============================================================

  // P1: Termination - every step decreases fuel
  @opaque
  def terminationLemma(vm: VM, instr: Instr): Unit = {
    require(vm.fuel > 0)

    step(vm, instr) match {
      case Ok(vm1) => assert(vm1.fuel < vm.fuel)
      case Err(_) => ()
    }
  }.ensuring(_ => true)

  // P3: Stack bounds - stack grows by at most 1
  @opaque
  def stackBoundsLemma(vm: VM, instr: Instr): Unit = {
    require(vm.fuel > 0)

    step(vm, instr) match {
      case Ok(vm1) => assert(vm1.stack.size <= vm.stack.size + 1)
      case Err(_) => ()
    }
  }.ensuring(_ => true)

  // P5: Zero fuel always fails
  @opaque
  def fuelExhaustionLemma(vm: VM, program: List[Instr]): Unit = {
    require(vm.fuel == 0)
    require(!program.isEmpty)

    run(vm, program) match {
      case Err(msg) => assert(msg == "fuel exhausted")
      case Ok(_) => assert(false) // unreachable
    }
  }.ensuring(_ => true)

  // ============================================================
  // Test Cases (as assertions)
  // ============================================================

  def testT1_BasicComparison(): Unit = {
    val program = List[Instr](Push(VInt(3)), Push(VInt(5)), Lte)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    assert(result == Ok(VM(List(VBool(true)), BigInt(7))))
  }

  def testT2_BooleanLogic(): Unit = {
    val program = List[Instr](Push(VBool(true)), Push(VBool(false)), And)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    result match {
      case Ok(vm1) => assert(vm1.stack == List[Value](VBool(false)))
      case Err(_) => assert(false)
    }
  }

  def testT3_StackManipulation(): Unit = {
    val program = List[Instr](Push(VInt(1)), Push(VInt(2)), Swap, Drop)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    result match {
      case Ok(vm1) => assert(vm1.stack == List[Value](VInt(2)))
      case Err(_) => assert(false)
    }
  }

  def testT4_Conditional(): Unit = {
    val program = List[Instr](
      Push(VBool(true)),
      IfElse(List(Push(VInt(1))), List(Push(VInt(2))))
    )
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    result match {
      case Ok(vm1) => assert(vm1.stack == List[Value](VInt(1)))
      case Err(_) => assert(false)
    }
  }

  def testT5_TypeError(): Unit = {
    val program = List[Instr](Push(VInt(1)), Push(VBool(true)), And)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    assert(result == Err[VM]("type: And requires bool bool"))
  }

  def testT6_Underflow(): Unit = {
    val program = List[Instr](Drop)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    assert(result == Err[VM]("underflow: Drop requires 1 element"))
  }

  def testT7_FuelExhaustion(): Unit = {
    val program = List[Instr](Push(VInt(1)), Push(VInt(2)), Push(VInt(3)))
    val vm = VM(Nil(), BigInt(2))
    val result = run(vm, program)
    assert(result == Err[VM]("fuel exhausted"))
  }

  def testT8_EqualitySameType(): Unit = {
    val program = List[Instr](Push(VInt(5)), Push(VInt(5)), Eq)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    result match {
      case Ok(vm1) => assert(vm1.stack == List[Value](VBool(true)))
      case Err(_) => assert(false)
    }
  }

  def testT9_EqualityDifferentTypes(): Unit = {
    val program = List[Instr](Push(VInt(1)), Push(VBool(true)), Eq)
    val vm = VM(Nil(), BigInt(10))
    val result = run(vm, program)
    assert(result == Err[VM]("type: Eq requires same types"))
  }

  def testT10_CompoundExpression(): Unit = {
    // (3 <= 5) AND (NOT false)
    val program = List[Instr](
      Push(VInt(3)),
      Push(VInt(5)),
      Lte,
      Push(VBool(false)),
      Not,
      And
    )
    val vm = VM(Nil(), BigInt(20))
    val result = run(vm, program)
    result match {
      case Ok(vm1) =>
        assert(vm1.stack == List[Value](VBool(true)))
        assert(vm1.fuel == BigInt(14))
      case Err(_) => assert(false)
    }
  }
}
