import React from 'react'
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import "./Home.css"
import Navi from '../navibar/Navi';

function Home() {

    return (
      <div>
        <Navi/>
          
      <div className='background'>
          <center><h1>Home</h1></center> 
          <div className='form'>
          <Form>
              <Form.Group className="mb-3" controlId="formBasicEmail">
                  <Form.Select >
                      <option>Select the Quantity Type</option>
                      <option>BTC</option>
                      <option>USDT</option>
                      <option>ETHEREUM</option>
                      <option>LITECOIN</option>
                      <option>RIPPLE</option>
                  </Form.Select>
                  
              </Form.Group>
  
  
              <Form.Group className="mb-3" >
                  <Form.Label>Enter Quantity</Form.Label>
                  <Form.Control type="text"  />
                  
              </Form.Group>
  
              <Form.Group className="mb-3" >
                  <Form.Select >
                      <option>Select the Symbol</option>
                      <option>BTCUSDT</option>
                  </Form.Select>
                  
              </Form.Group>
              <Form.Group className="mb-3">
                  <Form.Label>Enter Leverage</Form.Label>
                  <Form.Control type="text"  />
                  
              </Form.Group>
              <center>
                      <Button variant="primary" type="submit">
                          Place Order
                      </Button>
              </center>
              
              </Form>
          </div>
          </div>  
      </div>
    )
  }
  
  export default Home