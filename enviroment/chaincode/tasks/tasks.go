package main

import (
    "github.com/hyperledger/fabric-chaincode-go/shim"
    "github.com/hyperledger/fabric-protos-go/peer"
)

type TaskChaincode struct{}

func (t *TaskChaincode) Init(stub shim.ChaincodeStubInterface) peer.Response {
    return shim.Success(nil)
}

func (t *TaskChaincode) Invoke(stub shim.ChaincodeStubInterface) peer.Response {
    fn, args := stub.GetFunctionAndParameters()
    
    switch fn {
    case "RegisterTask":
        if len(args) != 2 {
            return shim.Error("Incorrect number of arguments")
        }
        err := stub.PutState(args[0], []byte(args[1]))
        if err != nil {
            return shim.Error(err.Error())
        }
        return shim.Success([]byte(args[0]))
        
    case "CompleteTask":
        if len(args) != 2 {
            return shim.Error("Incorrect number of arguments")
        }
        value, err := stub.GetState(args[0])
        if err != nil {
            return shim.Error(err.Error())
        }
        if value == nil {
            return shim.Error("Task not found")
        }
        newValue := string(value) + ":" + args[1]
        err = stub.PutState(args[0], []byte(newValue))
        if err != nil {
            return shim.Error(err.Error())
        }
        return shim.Success([]byte(newValue))
        
    case "GetTask":
        if len(args) != 1 {
            return shim.Error("Incorrect number of arguments")
        }
        value, err := stub.GetState(args[0])
        if err != nil {
            return shim.Error(err.Error())
        }
        if value == nil {
            return shim.Error("Task not found")
        }
        return shim.Success(value)
    }
    
    return shim.Error("Unknown function")
}

func main() {
    err := shim.Start(new(TaskChaincode))
    if err != nil {
        panic(err)
    }
}
