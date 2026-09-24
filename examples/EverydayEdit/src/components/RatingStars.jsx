import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function RatingStars({rating=4,count=12}) { return <View accessibilityLabel={rating+' out of 5 stars, '+count+' reviews'} style={{flexDirection:'row',gap:6}}><Text style={{color:'#be9344'}}>{'★'.repeat(Math.max(0,Math.min(5,Math.round(rating))))}{'☆'.repeat(5-Math.max(0,Math.min(5,Math.round(rating))))}</Text><Text style={{color:'#888'}}>({count})</Text></View>; }
