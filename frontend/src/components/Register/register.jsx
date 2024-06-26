import React from 'react'
import './Register.css'
import axios from 'axios'
import  loading from '../../loading2.gif'

const BASE_URL = "http://localhost:5000"

export default function Register({setIsRegisterring, setIsLoggingIn}) {
    const [email, setEmail] = React.useState("")
    const [firstName, setFirstName] = React.useState("")
    const [lastName, setLastName] = React.useState("")
    const [password, setPassword] = React.useState("")
    const [isLoading, setIsLoading] = React.useState(false)
    const [confirmPassword, setConfirmPassword] = React.useState("")

    
    function firstNameOnChange(e){
        setFirstName(e.target.value)
    }
    function lastNameOnChange(e){
        setLastName(e.target.value)
    }
    function emailOnChange(e){
        setEmail(e.target.value)
    }
    function passwordOnChange(e){
        setPassword(e.target.value)
    }
    function confirmPasswordOnChange(e){
        setConfirmPassword(e.target.value)
    }

    async function handleRegister(e){
        e.preventDefault()
        if(firstName.length !==0 && lastName.length !==0 && email.length !==0 && password.length !==0 && confirmPassword.length !==0){
            if(password===confirmPassword){
                try{
                    setIsLoading(true)
                    let response = await axios.post(`${BASE_URL}/register`, {
                        "email":email,
                        "first_name":firstName,
                        "last_name":lastName,
                        "password":password
                    })
                    console.log(response.data)

                    let data = response.data;
                    if(data!==undefined){
                        if(data.success){
                            alert("Registration Successful, please login")
                            handleLoginClick()
                        }else{
                            alert(data.error)
                        }
                    }
                    else{
                        alert("Something went wrong")
                    }
                }catch(e){
                    console.log(e)
                    alert(e.message)
                }
                finally{
                    setIsLoading(false)
                }
            }else{
                alert("Passwords do not match!")
            }
        }
        else{
            alert("All fields are required!")
        }

    }

    function handleLoginClick(){
        setIsLoggingIn(true)
        setIsRegisterring(false)
    }


  return (
    <div>
        {isLoading &&
            <div className='loading'>
                <img src={loading}></img>
            </div>}
        <div className="register-form">
            <h3>Register to Mela</h3>
            <form>
                <input type="text" value={firstName} onChange={firstNameOnChange} placeholder='First Name:' required/>
                <input type="text" value={lastName} onChange={lastNameOnChange} placeholder='Last Name:' required/>
                <input type="text" value={email} onChange={emailOnChange} placeholder='Email:' required/>
                <input type="password" value={password} onChange={passwordOnChange} placeholder='Password:' required/>
                <input type="password" value={confirmPassword} onChange={confirmPasswordOnChange} placeholder='Confirm Password:' required/>
                <div className="btnrow">
                    <button onClick={handleRegister}>Register</button>
                    <button className='loginbtn' onClick={handleLoginClick}>Login</button>
                </div>
                
            </form>
        </div>
    </div>
  )
}
