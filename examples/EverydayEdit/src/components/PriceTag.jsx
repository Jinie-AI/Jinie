import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function PriceTag({amount=1990,currency='Rs.',originalPrice}) { return <View style={{flexDirection:'row',gap:8}}><Text style={{fontSize:20,fontWeight:'700'}}>{currency} {amount.toLocaleString()}</Text>{originalPrice>amount&&<Text style={{textDecorationLine:'line-through',color:'#888'}}>{currency} {originalPrice.toLocaleString()}</Text>}</View>; }
