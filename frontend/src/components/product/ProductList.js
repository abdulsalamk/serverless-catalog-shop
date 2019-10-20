import React, { Component } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { withTheme } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';

const Wrapper = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 40px;
  > a {
    text-decoration: none;
  }
  @media (max-width: 650px) {
    grid-template-columns: repeat(1, 1fr);
    grid-gap: 20px;
  }
`;
const LargeIMG = styled.div`
  background-image: url(${props => props.img});
  background-color: #ddd;
  width: 100%;
  padding-bottom: 133%;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: 50%;
  display: inline-block;
  @media (min-width: 650px) {
    filter: grayscale(100%);
    transition: filter .5s;
    &:hover {
      filter: grayscale(0);
    }
  }
`;
const ImgWrapper = styled.div`
  border-bottom: 3px solid ${props => props.borderColor};
  display: flex;
`;
const Title = styled.div`
  color: black;
  text-decoration-color: #FF7400;
  margin-top: 10px;
  @media (max-width: 650px) {
    font-size: 14px;
  }
`;
const Price = styled.span`
  display: block;
  color: #888;
  font-size: 14px;
  margin-top: 5px;
`;

class ProductList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      products: [],
      isLoading: true
    }
  }
  componentDidMount() {
    // fetch('https://aj6vbw5suc.execute-api.eu-west-1.amazonaws.com/dev/items')
    fetch('https://2yk3rknfyb.execute-api.eu-west-2.amazonaws.com/dev/items')
      .then(res => res.json())
      .then(products => {
        this.setState({ products, isLoading: false })
      }).catch(error => console.error('Error:', error))
  }
  render() {
    const { products, isLoading } = this.state;
    return (
      <Wrapper>
        {isLoading && <p></p>}
        {isLoading && <CircularProgress style={{margin:'auto'}} size={50} thickness={5} />}
        { products.map((product,i) => {
          return <Link key={i} to={`/product/${product.item_id}`}>
            <ImgWrapper borderColor={this.props.theme.palette.secondary.main}>
              <LargeIMG img={product.link}/>
            </ImgWrapper>
            <Title>
              {product.name}
              <Price>${product.price}</Price>
            </Title>
          </Link>
        })}
      </Wrapper>
    );
  }
};
export default withTheme()(ProductList);