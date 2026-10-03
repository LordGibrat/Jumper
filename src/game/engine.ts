import type {Phase,Progress,Shoe} from '../types'; import {CITIES,SHOES} from './levels';
export const GRAVITY=.4, EDGE=14;
export function shoe(p:Progress):Shoe{return SHOES.find(x=>x.id===p.shoe)||SHOES[0]}
export function people(a:number){return Math.floor(Math.sqrt(Math.max(a,0)))}
export function auraTier(a:number){return a<0?'Outsider':a<1000?'Rookie':a<10000?'Known':a<100000?'Star':a<1e6?'Legend':'Mega Legend'}
export function launch(power:number,p:Progress){const s=shoe(p);return {vx:(3+power/20)*s.speed,vy:(-6-power/10)*s.jump}}
export function computeTrajectory(startX:number,startY:number,startVx:number,startVy:number,maxDots=22,stepFrames=3){const points:{x:number;y:number}[]=[];let x=startX,y=startY,vx=startVx,vy=startVy,frame=0;while(points.length<maxDots){x+=vx;y+=vy;vy+=.4;frame+=1;if(frame%stepFrames===0)points.push({x,y});if(y>600||x>820)break}return points}
export function landingReward(p:Progress,flips:number){const bonus=flips*(p.flipMode==='back'?1.5:1);const score=50+Math.floor(bonus*100), aura=Math.min(1e6,p.aura+Math.floor(25*3**(p.landings+1)*(1+bonus)));const coins=Math.floor((10+5*(p.level+1)+Math.floor(bonus*20)+people(aura)/10)*shoe(p).coins);return {score,aura,coins,bonus}}
export function nextPad(p:Progress):Progress{const pads=CITIES[p.city].levels[p.level].pads; if(p.pad+1<pads.length)return {...p,pad:p.pad+1}; if(p.level+1<5)return {...p,level:p.level+1,pad:0}; if(p.city+1<CITIES.length)return {...p,city:p.city+1,level:0,pad:0,unlockedMax:Math.max(p.unlockedMax,p.city+1)}; return p}
export function reviveCost(p:Progress){return 100+(p.stats.attempts*0)+60*(p.level+1)}
export function missPenalty(p:Progress,factor=1){return Math.max(-1000000,p.aura-Math.floor((200*(p.level+1)+.4*Math.max(p.aura,0))*factor))}
