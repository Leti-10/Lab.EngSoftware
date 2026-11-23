import { averageOf } from './reviews'

describe('averageOf', () => {
  it('calcula a média das notas', () => {
    expect(averageOf([4, 5])).toBe(4.5)
  })

  it('devolve zero sem notas', () => {
    expect(averageOf([])).toBe(0)
  })
})
